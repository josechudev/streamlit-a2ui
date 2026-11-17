import type { ReactCatalogComponent } from "@a2ui/react";
import {
  MessageProcessor,
  type A2uiErrorPayload,
  type ActionPayload,
  type Subscription,
  type SurfaceModel,
} from "@a2ui/web_core";
import { basicCatalog } from "@a2ui/web_core/catalogs/basic/v1";

/** An A2UI wire message. Python never looks inside; neither do we, much. */
export type WireMessage = { readonly [key: string]: unknown };

export type Processor = MessageProcessor<ReactCatalogComponent>;
export type Surface = SurfaceModel<ReactCatalogComponent>;

/** One processing or surface error, as shown in the component. */
export type Notice = {
  readonly code: string;
  readonly message: string;
  readonly surfaceId?: string;
};

/** Everything the view needs. Replaced, never mutated, on each change. */
export type Snapshot = {
  /** Bumped on every replay, so the view remounts surfaces from scratch. */
  readonly generation: number;
  readonly surfaces: readonly Surface[];
  /** True once any surface has its root component. */
  readonly hasRoot: boolean;
  /** The most recent notices, oldest first. */
  readonly notices: readonly Notice[];
  /** Notices seen since the last replay, including ones no longer kept. */
  readonly noticeCount: number;
};

const MAX_NOTICES = 5;

// Bound here so the production build's dropConsole leaves it in place.
const warn: (...args: unknown[]) => void = console.warn.bind(console);

/** Wraps the action handler's bare payload in the 1.0 wire envelope. */
export function actionMessage(action: ActionPayload): WireMessage {
  return { version: "1.0", action };
}

/**
 * A 1.0 processor for the basic catalog. Actions are wrapped into wire
 * messages; outbound-listener messages (callAgentFunction, ...) are already
 * wire messages and are passed through unchanged.
 */
export function createProcessor(send: (message: WireMessage) => void): Processor {
  return new MessageProcessor<ReactCatalogComponent>(
    [basicCatalog],
    (action) => send(actionMessage(action)),
    { version: "1.0", outboundListener: (message) => send(message) },
  );
}

/**
 * Projects an append-only message log onto a processor.
 *
 * `sync(log)` hands the processor only the entries after the cursor. If the
 * log no longer extends what was processed (it shrank, or the entry before
 * the cursor changed), the processor is disposed and the log is replayed
 * from zero, so the rendered UI stays a pure function of the log.
 */
export class LogSession {
  private processor: Processor;
  private cursor = 0;
  /** JSON of `log[cursor - 1]`, to tell an appended log from a replaced one. */
  private lastProcessed: string | undefined;
  private generation = 0;
  private notices: Notice[] = [];
  private noticeCount = 0;
  private processorSubscriptions: Subscription[] = [];
  private readonly surfaceSubscriptions = new Map<string, Subscription>();
  private readonly listeners = new Set<() => void>();
  private snapshot: Snapshot;
  private disposed = false;

  constructor(private readonly newProcessor: () => Processor) {
    this.processor = this.attach(newProcessor());
    this.snapshot = this.buildSnapshot();
  }

  /** Processes whatever part of `log` has not been processed yet. */
  sync(log: readonly unknown[]): void {
    if (this.disposed) return;
    if (!this.extendsProcessed(log)) this.replay();
    if (log.length > this.cursor) {
      const tail = log.slice(this.cursor);
      // Errors are reported through the surface and model error events, which
      // also carry errors raised while rendering; the return value repeats them.
      this.processor.processMessagesWithErrors(tail);
      this.cursor = log.length;
      this.lastProcessed = JSON.stringify(log[log.length - 1]);
    }
    this.publish();
  }

  readonly subscribe = (listener: () => void): (() => void) => {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  };

  readonly getSnapshot = (): Snapshot => this.snapshot;

  dispose(): void {
    if (this.disposed) return;
    this.disposed = true;
    this.detach();
    this.listeners.clear();
  }

  private extendsProcessed(log: readonly unknown[]): boolean {
    if (this.cursor === 0) return true;
    if (log.length < this.cursor) return false;
    return JSON.stringify(log[this.cursor - 1]) === this.lastProcessed;
  }

  private replay(): void {
    this.detach();
    this.processor = this.attach(this.newProcessor());
    this.cursor = 0;
    this.lastProcessed = undefined;
    this.generation += 1;
    this.notices = [];
    this.noticeCount = 0;
  }

  private attach(processor: Processor): Processor {
    this.processorSubscriptions = [
      processor.model.onError.subscribe((error) => this.report(error)),
      processor.onSurfaceCreated((surface) => {
        this.surfaceSubscriptions.set(
          surface.id,
          surface.onError.subscribe((error) => this.report(error)),
        );
      }),
      processor.onSurfaceDeleted((id) => {
        this.surfaceSubscriptions.get(id)?.unsubscribe();
        this.surfaceSubscriptions.delete(id);
      }),
    ];
    return processor;
  }

  private detach(): void {
    for (const subscription of this.processorSubscriptions) {
      subscription.unsubscribe();
    }
    for (const subscription of this.surfaceSubscriptions.values()) {
      subscription.unsubscribe();
    }
    this.processorSubscriptions = [];
    this.surfaceSubscriptions.clear();
    this.processor.dispose();
  }

  private report(error: A2uiErrorPayload): void {
    warn("[streamlit-a2ui] A2UI error", error);
    const notice: Notice = {
      code: String(error.code),
      message: String(error.message),
      ...(typeof error.surfaceId === "string" && { surfaceId: error.surfaceId }),
    };
    this.notices = [...this.notices, notice].slice(-MAX_NOTICES);
    this.noticeCount += 1;
    this.publish();
  }

  private publish(): void {
    const next = this.buildSnapshot();
    const prev = this.snapshot;
    if (
      next.generation === prev.generation &&
      next.hasRoot === prev.hasRoot &&
      next.notices === prev.notices &&
      next.surfaces.length === prev.surfaces.length &&
      next.surfaces.every((surface, i) => surface === prev.surfaces[i])
    ) {
      return;
    }
    this.snapshot = next;
    for (const listener of this.listeners) listener();
  }

  private buildSnapshot(): Snapshot {
    const surfaces = [...this.processor.getSurfaces().values()];
    return {
      generation: this.generation,
      surfaces,
      hasRoot: surfaces.some(
        (surface) => surface.componentsModel.get(surface.rootId) !== undefined,
      ),
      notices: this.notices,
      noticeCount: this.noticeCount,
    };
  }
}
