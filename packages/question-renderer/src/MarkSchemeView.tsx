import type { ReactNode } from "react";
import { DocView } from "./DocView";
import type { MarkPointOut, NoteOut } from "./types";

export interface MarkSchemeViewProps {
  markPoints: MarkPointOut[];
  notes: NoteOut[];
  marks: number;
  marksCapped: boolean;
}

const NOTE_PREFIX: Record<NoteOut["kind"], string | null> = {
  general: null,
  owtte: "OWTTE",
  accept: "Accept",
  do_not_accept: "Do not accept",
  cap: "Max",
  ecf: "ECF",
};

/** One entry of the list: a single mark point, or the alternatives of one mark joined by OR. */
interface Entry {
  alternatives: MarkPointOut[];
}

/** Groups by alternative_group, in order of first appearance. */
function toEntries(points: MarkPointOut[]): Entry[] {
  const entries: Entry[] = [];
  const byGroup = new Map<string, Entry>();
  for (const point of points) {
    const group = point.alternative_group;
    if (group) {
      const existing = byGroup.get(group);
      if (existing) {
        existing.alternatives.push(point);
        continue;
      }
      const entry: Entry = { alternatives: [point] };
      byGroup.set(group, entry);
      entries.push(entry);
    } else {
      entries.push({ alternatives: [point] });
    }
  }
  return entries;
}

type Item = { kind: "entry"; entry: Entry } | { kind: "route"; route: string; entries: Entry[] };

/** Top-level items in order of first appearance; points sharing a route are gathered into one route item. */
function toItems(points: MarkPointOut[]): Item[] {
  const items: Item[] = [];
  const routes = new Map<string, MarkPointOut[]>();
  const loose: MarkPointOut[] = [];
  // Walk once to place route blocks and loose points in order of first appearance.
  const order: ({ loose: true; index: number } | { loose: false; route: string })[] = [];
  for (const point of points) {
    if (point.route) {
      if (!routes.has(point.route)) {
        routes.set(point.route, []);
        order.push({ loose: false, route: point.route });
      }
      routes.get(point.route)!.push(point);
    } else {
      loose.push(point);
      order.push({ loose: true, index: loose.length - 1 });
    }
  }
  // Alternative groups among loose points keep their first position.
  const looseEntries = toEntries(loose);
  const emitted = new Set<Entry>();
  const entryOf = new Map<MarkPointOut, Entry>();
  for (const entry of looseEntries) for (const alt of entry.alternatives) entryOf.set(alt, entry);
  for (const slot of order) {
    if (slot.loose) {
      const entry = entryOf.get(loose[slot.index]!)!;
      if (!emitted.has(entry)) {
        emitted.add(entry);
        items.push({ kind: "entry", entry });
      }
    } else {
      items.push({ kind: "route", route: slot.route, entries: toEntries(routes.get(slot.route)!) });
    }
  }
  return items;
}

function NoteLine({ note }: { note: NoteOut }) {
  const prefix = NOTE_PREFIX[note.kind];
  return (
    <li className={`qr-ms-note qr-ms-note-${note.kind.replace(/_/g, "-")}`}>
      {prefix && <span className="qr-ms-note-kind">{prefix}</span>}
      <div className="qr-ms-note-body">
        <DocView doc={note.content} />
      </div>
    </li>
  );
}

function AcceptRange({ range }: { range: NonNullable<MarkPointOut["accept_range"]> }) {
  return (
    <p className="qr-ms-accept">
      Accept {range.minimum}–{range.maximum}
      {range.unit ? ` ${range.unit}` : ""}
    </p>
  );
}

/** A part's mark points and notes. */
export function MarkSchemeView({ markPoints, notes, marks, marksCapped }: MarkSchemeViewProps) {
  const pointIds = new Set(markPoints.map((point) => point.id));
  const attached = new Map<string, NoteOut[]>();
  const general: NoteOut[] = [];
  for (const note of notes) {
    if (note.mark_point_id && pointIds.has(note.mark_point_id)) {
      const list = attached.get(note.mark_point_id) ?? [];
      list.push(note);
      attached.set(note.mark_point_id, list);
    } else {
      general.push(note);
    }
  }

  const renderEntry = (entry: Entry, key: number): ReactNode => (
    <li key={key} className="qr-ms-point">
      <span className="qr-ms-tick" aria-hidden="true">
        {"✓"}
      </span>
      <span className="qr-sr-only">mark point</span>
      <div className="qr-ms-point-body">
        {entry.alternatives.map((point, index) => (
          <div key={point.id} className="qr-ms-alternative">
            {index > 0 && <p className="qr-ms-or">OR</p>}
            <DocView doc={point.content} />
            {point.accept_range && <AcceptRange range={point.accept_range} />}
            {attached.has(point.id) && (
              <ul className="qr-ms-notes qr-ms-notes-attached">
                {attached.get(point.id)!.map((note, i) => (
                  <NoteLine key={i} note={note} />
                ))}
              </ul>
            )}
          </div>
        ))}
      </div>
    </li>
  );

  const items = toItems(markPoints);
  let routeNumber = 0;

  return (
    <div className="qr-markscheme" role="group" aria-label="Mark scheme">
      <p className="qr-ms-title">
        <span>Mark scheme</span> <span className="qr-ms-marks">{marksCapped ? `[max ${marks}]` : `[${marks}]`}</span>
      </p>
      {items.length > 0 && (
        <ol className="qr-ms-points">
          {items.map((item, index) => {
            if (item.kind === "entry") return renderEntry(item.entry, index);
            routeNumber += 1;
            return (
              <li key={index} className="qr-ms-route">
                <p className="qr-ms-route-label">{`Method ${routeNumber}`}</p>
                <ol className="qr-ms-points">{item.entries.map((entry, i) => renderEntry(entry, i))}</ol>
              </li>
            );
          })}
        </ol>
      )}
      {general.length > 0 && (
        <ul className="qr-ms-notes">
          {general.map((note, index) => (
            <NoteLine key={index} note={note} />
          ))}
        </ul>
      )}
    </div>
  );
}
