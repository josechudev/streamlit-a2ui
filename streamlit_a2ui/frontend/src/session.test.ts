import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";

import { describe, expect, it, vi } from "vitest";

import {
  actionMessage,
  createProcessor,
  LogSession,
  type Processor,
  type WireMessage,
} from "./session";

/** Messages from a sample shipped with the installed web_core 1.0 schemas. */
function sample(name: string): WireMessage[] {
  const path = fileURLToPath(
    new URL(
      `../node_modules/@a2ui/web_core/src/v1_0/schemas/catalogs/basic/examples/${name}.json`,
      import.meta.url,
    ),
  );
  return (JSON.parse(readFileSync(path, "utf8")) as { messages: WireMessage[] })
    .messages;
}

/** A session over real processors, recording each one it creates. */
function trackedSession(): { session: LogSession; processors: Processor[] } {
  const processors: Processor[] = [];
  const session = new LogSession(() => {
    const processor = createProcessor(() => {});
    vi.spyOn(processor, "processMessagesWithErrors");
    vi.spyOn(processor, "dispose");
    processors.push(processor);
    return processor;
  });
  return { session, processors };
}

const login = sample("00_simple-login-form");
const incremental = sample("00_incremental");

describe("LogSession", () => {
  it("processes only the unprocessed tail of the log", () => {
    const { session, processors } = trackedSession();
    const [processor] = processors;

    session.sync(incremental.slice(0, 2));
    session.sync(incremental.slice(0, 2));
    session.sync(incremental.slice(0, 4));

    expect(processors).toHaveLength(1);
    const calls = vi.mocked(processor.processMessagesWithErrors).mock.calls;
    expect(calls.map(([messages]) => messages)).toEqual([
      incremental.slice(0, 2),
      incremental.slice(2, 4),
    ]);
  });

  it("disposes the processor and replays from zero when the log shrinks", () => {
    const { session, processors } = trackedSession();
    session.sync(incremental);
    const before = session.getSnapshot().generation;

    session.sync(login);

    expect(processors).toHaveLength(2);
    expect(processors[0].dispose).toHaveBeenCalledOnce();
    expect(processors[1].processMessagesWithErrors).toHaveBeenCalledWith(login);
    const snapshot = session.getSnapshot();
    expect(snapshot.generation).toBe(before + 1);
    expect(snapshot.surfaces.map((surface) => surface.id)).toEqual([
      "gallery-simple-login-form",
    ]);
  });

  it("replays when the processed prefix was replaced, even if longer", () => {
    const { session, processors } = trackedSession();
    session.sync(login);

    session.sync([...incremental]);

    expect(processors).toHaveLength(2);
    expect(processors[1].processMessagesWithErrors).toHaveBeenCalledWith(
      incremental,
    );
  });

  it("reports a rejected message and keeps processing later ones", async () => {
    const { session } = trackedSession();
    const invalid = {
      version: "1.0",
      updateComponents: { surfaceId: "nowhere", components: [] },
    };

    session.sync([invalid, ...login]);
    await Promise.resolve();

    const snapshot = session.getSnapshot();
    expect(snapshot.noticeCount).toBe(1);
    expect(snapshot.notices[0].code).toEqual(expect.any(String));
    expect(snapshot.notices[0].message).not.toBe("");
    expect(snapshot.hasRoot).toBe(true);
  });

  it("waits until a surface has its root component", () => {
    const { session } = trackedSession();
    session.sync(login.slice(0, 1));
    expect(session.getSnapshot().surfaces).toHaveLength(1);
    expect(session.getSnapshot().hasRoot).toBe(false);

    session.sync(login);
    expect(session.getSnapshot().hasRoot).toBe(true);
  });
});

describe("outbound messages", () => {
  it("wraps an ActionPayload in the 1.0 wire shape", async () => {
    const send = vi.fn<(message: WireMessage) => void>();
    const processor = createProcessor(send);
    processor.processMessagesWithErrors(login);
    const surface = processor.getSurface("gallery-simple-login-form");
    expect(surface).toBeDefined();

    await surface?.dispatchAction(
      { event: { name: "login_submitted", context: { user: "ada" } } },
      "submit_button",
    );

    expect(send).toHaveBeenCalledOnce();
    const [message] = send.mock.calls[0];
    expect(message).toMatchObject({
      version: "1.0",
      action: {
        name: "login_submitted",
        surfaceId: "gallery-simple-login-form",
        sourceComponentId: "submit_button",
        context: { user: "ada" },
      },
    });
    processor.dispose();
  });

  it("builds the envelope around the payload without changing it", () => {
    const payload = {
      name: "n",
      surfaceId: "s",
      sourceComponentId: "c",
      timestamp: "2026-11-17T00:00:00.000Z",
      context: {},
    };
    const message = actionMessage(payload);
    expect(message).toEqual({ version: "1.0", action: payload });
    expect(message.action).toBe(payload);
  });

  it("passes outbound-listener messages through unchanged", async () => {
    const send = vi.fn<(message: WireMessage) => void>();
    const processor = createProcessor(send);
    processor.processMessagesWithErrors(login);

    const pending = processor.callAgentFunction(
      "gallery-simple-login-form",
      { call: "lookup", args: { q: "x" } },
      { functionCallId: "call-1", timeoutMs: 1000 },
    );
    pending.catch(() => {});

    // Exactly the renderer_to_agent.json envelope web_core emits: not wrapped
    // in an action, no fields added or removed.
    expect(send).toHaveBeenCalledOnce();
    expect(send.mock.calls[0][0]).toStrictEqual({
      version: "1.0",
      callAgentFunction: {
        surfaceId: "gallery-simple-login-form",
        functionCallId: "call-1",
        callFunction: { "@call": "lookup", args: { q: "x" } },
      },
    });
    processor.dispose();
    await expect(pending).rejects.toBeDefined();
  });
});
