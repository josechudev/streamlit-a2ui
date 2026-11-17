import {
  FrontendRenderer,
  FrontendRendererArgs,
} from "@streamlit/component-v2-lib";
import { StrictMode } from "react";
import { createRoot, Root } from "react-dom/client";

import { createProcessor, LogSession, type WireMessage } from "./session";
import Surfaces from "./Surfaces";
import "./theme.css";

type StateShape = { renderer_message: WireMessage };
type DataShape = { messages: unknown[] } | null | undefined;
type Args = FrontendRendererArgs<StateShape, DataShape>;

type Instance = {
  root: Root;
  session: LogSession;
  /** Streamlit passes a new setter on every call; keep the latest. */
  setTrigger: Args["setTriggerValue"];
};

const instances = new WeakMap<Args["parentElement"], Instance>();

/*
 * The basic catalog's custom elements are registered once per page. A second
 * copy of this bundle (for example a rebuilt one, loaded without a page
 * reload) would register the same tag names with different classes, which
 * throws while rendering. The first copy to load claims the page; any later
 * copy renders a notice instead of surfaces.
 */
const BUNDLE_CLAIM = Symbol.for("streamlit-a2ui.bundle");
const thisBundle = {};
const claims = globalThis as { [BUNDLE_CLAIM]?: object };
claims[BUNDLE_CLAIM] ??= thisBundle;
const ownsPage = claims[BUNDLE_CLAIM] === thisBundle;

/** Plain JSON for the trigger: drops undefined fields and class instances. */
function toJson(message: WireMessage): WireMessage {
  return JSON.parse(JSON.stringify(message)) as WireMessage;
}

const A2uiSurfaceRoot: FrontendRenderer<StateShape, DataShape> = ({
  data,
  parentElement,
  setTriggerValue,
}) => {
  const host = parentElement.querySelector(".a2ui-host");
  if (!host) {
    throw new Error("streamlit-a2ui: .a2ui-host element not found");
  }

  if (!ownsPage) {
    host.textContent =
      "Another build of streamlit-a2ui is already loaded on this page. Reload the page.";
    host.classList.add("a2ui-notice");
    return;
  }

  let instance = instances.get(parentElement);
  if (!instance) {
    const send = (message: WireMessage): void => {
      instances
        .get(parentElement)
        ?.setTrigger("renderer_message", toJson(message));
    };
    const session = new LogSession(() => createProcessor(send));
    const root = createRoot(host);
    root.render(
      <StrictMode>
        <Surfaces session={session} />
      </StrictMode>,
    );
    instance = { root, session, setTrigger: setTriggerValue };
    instances.set(parentElement, instance);
  } else {
    instance.setTrigger = setTriggerValue;
  }
  instance.session.sync(data?.messages ?? []);

  return () => {
    const current = instances.get(parentElement);
    if (!current) return;
    instances.delete(parentElement);
    current.root.unmount();
    current.session.dispose();
  };
};

export default A2uiSurfaceRoot;
