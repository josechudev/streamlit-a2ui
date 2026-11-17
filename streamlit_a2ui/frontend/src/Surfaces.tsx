import { renderMarkdown } from "@a2ui/markdown-it";
import {
  A2uiSurface,
  MarkdownContext,
  type ReactCatalogComponent,
} from "@a2ui/react";
import type { MessageProcessor, SurfaceModel } from "@a2ui/web_core";
import { FC, ReactElement, useEffect, useState } from "react";

type Props = { processor: MessageProcessor<ReactCatalogComponent> };

const listSurfaces = (
  processor: Props["processor"],
): SurfaceModel<ReactCatalogComponent>[] => [
  ...processor.getSurfaces().values(),
];

/** Renders every surface the processor holds, in creation order. */
const Surfaces: FC<Props> = ({ processor }): ReactElement => {
  const [surfaces, setSurfaces] = useState(() => listSurfaces(processor));

  useEffect(() => {
    const sync = (): void => setSurfaces(listSurfaces(processor));
    const created = processor.onSurfaceCreated(sync);
    const deleted = processor.onSurfaceDeleted(sync);
    sync();
    return () => {
      created.unsubscribe();
      deleted.unsubscribe();
    };
  }, [processor]);

  if (surfaces.length === 0) {
    return <div className="a2ui-waiting">Waiting for the agent…</div>;
  }

  return (
    <MarkdownContext.Provider value={renderMarkdown}>
      {surfaces.map((surface) => (
        // A2uiSurface renders nothing until the root component arrives;
        // theme.css shows a waiting message while this wrapper is empty.
        <div key={surface.id} className="a2ui-surface">
          <A2uiSurface surface={surface} />
        </div>
      ))}
    </MarkdownContext.Provider>
  );
};

export default Surfaces;
