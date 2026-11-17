// @vitest-environment jsdom
import { act, FC, ReactElement } from "react";
import { createRoot, Root } from "react-dom/client";
import {
  afterEach,
  beforeAll,
  beforeEach,
  describe,
  expect,
  it,
  vi,
} from "vitest";

import type { LogSession, Snapshot, Surface } from "./session";

(
  globalThis as { IS_REACT_ACT_ENVIRONMENT?: boolean }
).IS_REACT_ACT_ENVIRONMENT = true;

vi.mock("@a2ui/react", async (importOriginal) => {
  const actual = await importOriginal<typeof import("@a2ui/react")>();
  const A2uiSurface: FC<{ surface: { id: string } }> = ({ surface }) => {
    if (surface.id === "bad") throw new Error("kaboom");
    return <p>{`surface ${surface.id}`}</p>;
  };
  return { ...actual, A2uiSurface };
});

// session.ts binds console.warn at import, so spy first and import after.
const warnSpy = vi.spyOn(console, "warn").mockImplementation(() => {});
let ErrorBoundary: typeof import("./ErrorBoundary").default;
let Surfaces: typeof import("./Surfaces").default;
beforeAll(async () => {
  ErrorBoundary = (await import("./ErrorBoundary")).default;
  Surfaces = (await import("./Surfaces")).default;
});

const roots: { root: Root; el: HTMLElement }[] = [];
function mount(ui: ReactElement) {
  const el = document.createElement("div");
  const root = createRoot(el);
  roots.push({ root, el });
  act(() => root.render(ui));
  return { el, root };
}

// React rethrows render errors on the window; jsdom would print each one.
const swallow = (e: ErrorEvent) => e.preventDefault();
beforeEach(() => {
  window.addEventListener("error", swallow);
  vi.spyOn(console, "error").mockImplementation(() => {});
});
afterEach(() => {
  for (const { root } of roots.splice(0)) act(() => root.unmount());
  window.removeEventListener("error", swallow);
  vi.mocked(console.error).mockRestore();
  warnSpy.mockClear();
});

function fakeSession(snapshot: Snapshot): LogSession {
  return {
    subscribe: () => () => {},
    getSnapshot: () => snapshot,
  } as unknown as LogSession;
}

describe("ErrorBoundary", () => {
  it("keeps other surfaces and the notices list rendered", () => {
    const surface = (id: string) => ({ id }) as unknown as Surface;
    const { el } = mount(
      <Surfaces
        session={fakeSession({
          generation: 0,
          surfaces: [surface("bad"), surface("good")],
          hasRoot: true,
          notices: [{ code: "E_TEST", message: "boom" }],
          noticeCount: 1,
        } as unknown as Snapshot)}
      />,
    );
    const texts = [...el.querySelectorAll(".a2ui-notice")].map(
      (n) => n.textContent,
    );
    expect(texts[0]).toBe('Surface "bad" failed to render: kaboom');
    expect(el.querySelector("p")?.textContent).toBe("surface good");
    expect(el.querySelector(".a2ui-notice-title")?.textContent).toBe(
      "1 A2UI error",
    );
    expect(el.querySelector(".a2ui-notice li")?.textContent).toContain("boom");
    expect(warnSpy).toHaveBeenCalled();
  });

  it("resets when its key changes", () => {
    let fail = true;
    const Maybe: FC = () => {
      if (fail) throw new Error("x");
      return <p>recovered</p>;
    };
    const ui = (gen: number) => (
      <ErrorBoundary key={`${gen}:a`} surfaceId="a">
        <Maybe />
      </ErrorBoundary>
    );
    const { el, root } = mount(ui(0));
    expect(el.querySelector(".a2ui-notice")).not.toBeNull();
    fail = false;
    act(() => root.render(ui(1)));
    expect(el.querySelector(".a2ui-notice")).toBeNull();
    expect(el.querySelector("p")?.textContent).toBe("recovered");
  });
});
