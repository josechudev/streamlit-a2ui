import { renderMarkdown } from "@a2ui/markdown-it";
import { A2uiSurface, MarkdownContext } from "@a2ui/react";
import { FC, ReactElement, useSyncExternalStore } from "react";

import type { LogSession, Snapshot } from "./session";

/** Plain-text list of processing and surface errors. Never renders HTML. */
const Notices: FC<{ snapshot: Snapshot }> = ({ snapshot }) => {
  const { notices, noticeCount } = snapshot;
  if (noticeCount === 0) return null;
  // Notices are numbered from the last replay; older ones have been dropped.
  const hidden = noticeCount - notices.length;
  return (
    <div className="a2ui-notice" role="status">
      <div className="a2ui-notice-title">
        {noticeCount === 1 ? "1 A2UI error" : `${noticeCount} A2UI errors`}
        {hidden > 0 ? ` (showing the last ${notices.length})` : ""}
      </div>
      <ul>
        {notices.map((notice, i) => (
          <li key={hidden + i}>
            {notice.code}
            {notice.surfaceId ? ` [${notice.surfaceId}]` : ""}: {notice.message}
          </li>
        ))}
      </ul>
    </div>
  );
};

/** Renders every surface the session's processor holds, in creation order. */
const Surfaces: FC<{ session: LogSession }> = ({ session }): ReactElement => {
  const snapshot = useSyncExternalStore(session.subscribe, session.getSnapshot);

  return (
    <>
      {!snapshot.hasRoot && (
        <div className="a2ui-waiting">Waiting for the agent…</div>
      )}
      <MarkdownContext.Provider value={renderMarkdown}>
        {snapshot.surfaces.map((surface) => (
          // A surface renders nothing until its root component arrives.
          <div
            key={`${snapshot.generation}:${surface.id}`}
            className="a2ui-surface"
          >
            <A2uiSurface surface={surface} />
          </div>
        ))}
      </MarkdownContext.Provider>
      <Notices snapshot={snapshot} />
    </>
  );
};

export default Surfaces;
