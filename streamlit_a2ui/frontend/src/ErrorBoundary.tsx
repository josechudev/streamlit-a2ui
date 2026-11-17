import { Component, ErrorInfo, ReactNode } from "react";

import { warn } from "./session";

type Props = { surfaceId: string; children: ReactNode };
type State = { error: Error | null };

/** Keeps one surface's render failure from taking down its siblings. */
export default class ErrorBoundary extends Component<Props, State> {
  state: State = { error: null };

  static getDerivedStateFromError(error: unknown): State {
    return { error: error instanceof Error ? error : new Error(String(error)) };
  }

  componentDidCatch(error: unknown, info: ErrorInfo): void {
    warn(
      `[streamlit-a2ui] surface "${this.props.surfaceId}" failed to render`,
      error,
      info.componentStack,
    );
  }

  render(): ReactNode {
    const { error } = this.state;
    if (!error) return this.props.children;
    return (
      <div className="a2ui-notice" role="status">
        {`Surface "${this.props.surfaceId}" failed to render: ${String(error.message)}`}
      </div>
    );
  }
}
