import { MessageProcessor } from "@a2ui/web_core";
import { basicCatalog } from "@a2ui/web_core/catalogs/basic/v1";
import type { ReactCatalogComponent } from "@a2ui/react";
import {
  FrontendRenderer,
  FrontendRendererArgs,
} from "@streamlit/component-v2-lib";
import { StrictMode } from "react";
import { createRoot, Root } from "react-dom/client";

import Surfaces from "./Surfaces";
import "./theme.css";

/** A renderer→agent or agent→renderer message. Python never looks inside. */
type WireMessage = Record<string, unknown>;

type StateShape = { renderer_message: WireMessage };
type DataShape = { messages: WireMessage[] } | null | undefined;

type Processor = MessageProcessor<ReactCatalogComponent>;

type Instance = {
  root: Root;
  processor: Processor;
  /** Number of log entries already handed to the processor. */
  cursor: number;
  /** Latest trigger setter; the renderer function receives a new one per call. */
  setTrigger: FrontendRendererArgs<StateShape, DataShape>["setTriggerValue"];
};

const instances: WeakMap<FrontendRendererArgs["parentElement"], Instance> =
  new WeakMap();

let processorsConstructed = 0;

function createProcessor(
  key: string,
  send: (message: WireMessage) => void,
): Processor {
  processorsConstructed += 1;
  console.info(
    `[streamlit-a2ui] MessageProcessor constructed #${processorsConstructed} (key=${key})`,
  );
  return new MessageProcessor<ReactCatalogComponent>(
    [basicCatalog],
    // The action handler receives the payload; wrap it in the 1.0 envelope
    // defined by renderer_to_agent.json.
    (action) => send({ version: "1.0", action }),
    {
      version: "1.0",
      // callAgentFunction / rendererFunctionResponse are already full messages.
      outboundListener: (message) => send(message),
    },
  );
}

function toPlainJson(message: WireMessage): WireMessage {
  return JSON.parse(JSON.stringify(message)) as WireMessage;
}

/** Sends one renderer→agent message to Python through the single trigger. */
function senderFor(
  parentElement: FrontendRendererArgs["parentElement"],
): (message: WireMessage) => void {
  return (message) => {
    instances
      .get(parentElement)
      ?.setTrigger("renderer_message", toPlainJson(message));
  };
}

const A2uiSurfaceRoot: FrontendRenderer<StateShape, DataShape> = (args) => {
  const { data, parentElement, setTriggerValue, key } = args;

  const rootElement = parentElement.querySelector(".a2ui-host");
  if (!rootElement) {
    throw new Error("Unexpected: .a2ui-host element not found");
  }

  let instance = instances.get(parentElement);
  if (!instance) {
    instance = {
      root: createRoot(rootElement),
      processor: createProcessor(key, senderFor(parentElement)),
      cursor: 0,
      setTrigger: setTriggerValue,
    };
    instances.set(parentElement, instance);
  }
  instance.setTrigger = setTriggerValue;

  const log = data?.messages ?? [];

  // A shorter log than we have seen means it was replaced, not appended to.
  // Replay from zero so the UI stays a pure function of the log.
  if (log.length < instance.cursor) {
    console.info("[streamlit-a2ui] log shrank; replaying from 0");
    instance.processor.dispose();
    instance.processor = createProcessor(key, senderFor(parentElement));
    instance.cursor = 0;
  }

  if (log.length > instance.cursor) {
    const tail = log.slice(instance.cursor);
    const errors = instance.processor.processMessagesWithErrors(tail);
    instance.cursor = log.length;
    for (const error of errors) {
      console.warn("[streamlit-a2ui] message rejected", error);
    }
  }

  instance.root.render(
    <StrictMode>
      <Surfaces processor={instance.processor} />
    </StrictMode>,
  );

  return () => {
    const current = instances.get(parentElement);
    if (current) {
      current.root.unmount();
      current.processor.dispose();
      instances.delete(parentElement);
    }
  };
};

export default A2uiSurfaceRoot;
