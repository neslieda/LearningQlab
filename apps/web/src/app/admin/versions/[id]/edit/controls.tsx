"use client";

import { useId, type ReactNode } from "react";
import type { Doc } from "@qlab/api-client";
import { DocEditor, type BlockName, type MarkName } from "@qlab/question-editor";
import { emptyDoc, isBlankDoc, type EditProblem } from "@/lib/edit-document";

const EMPTY = emptyDoc();

export const BTN = "rounded border border-[var(--page-border)] px-3 py-1.5 disabled:opacity-50";
export const INPUT = "rounded border border-[var(--page-border)] bg-transparent p-2";

export function fieldDomId(path: string): string {
  return `field-${path.replace(/[^A-Za-z0-9]+/g, "-")}`;
}

/** Moves focus to the first control of a field (used by the error summary). */
export function focusField(path: string): void {
  const root = document.getElementById(fieldDomId(path));
  root?.scrollIntoView?.({ block: "center" });
  // The text box before the toolbar buttons that sit in front of it.
  (root?.querySelector<HTMLElement>('[contenteditable="true"]') ?? root?.querySelector<HTMLElement>("input, select, textarea, button") ?? root)?.focus();
}

/** Wraps one field: an anchor for the error summary and the field's own problems, written next to it. */
export function FieldShell({ path, problems, children }: { path: string; problems: readonly EditProblem[]; children: (describedBy: string | undefined) => ReactNode }) {
  const own = problems.filter((p) => p.field === path);
  const errId = `${fieldDomId(path)}-errors`;
  return (
    <div id={fieldDomId(path)} className="space-y-1">
      {children(own.length > 0 ? errId : undefined)}
      {own.length > 0 ? (
        <ul id={errId} className="list-disc pl-5 text-sm text-red-700 dark:text-red-400">
          {own.map((p, i) => (
            <li key={i}>{p.message}</li>
          ))}
        </ul>
      ) : null}
    </div>
  );
}

export interface DocFieldProps {
  path: string;
  label: string;
  value: Doc | null | undefined;
  /** An optional document: a blank editor stores null. */
  optional?: boolean;
  onChange: (doc: Doc | null) => void;
  problems: readonly EditProblem[];
  blocks?: readonly BlockName[];
  marks?: readonly MarkName[];
}

export const TABLE_BLOCKS: readonly BlockName[] = ["math_block", "table", "bullet_list", "ordered_list"];
export const MARKSCHEME_MARKS: readonly MarkName[] = ["bold", "italic", "sub", "sup", "optional", "essential"];

export function DocField({ path, label, value, optional, onChange, problems, blocks, marks }: DocFieldProps) {
  return (
    <FieldShell path={path} problems={problems}>
      {(describedBy) => (
        <DocEditor
          value={value ?? EMPTY}
          label={label}
          allowedBlocks={blocks}
          allowMarks={marks}
          ariaDescribedBy={describedBy}
          onChange={(doc) => onChange(optional && isBlankDoc(doc) ? null : doc)}
        />
      )}
    </FieldShell>
  );
}

export function SelectControl<T extends string | number>({
  path,
  label,
  value,
  options,
  onChange,
  problems,
  disabled,
}: {
  path: string;
  label: string;
  value: T | "";
  options: ReadonlyArray<{ value: T | ""; text: string }>;
  onChange: (value: T | "") => void;
  problems: readonly EditProblem[];
  disabled?: boolean;
}) {
  const id = useId();
  return (
    <FieldShell path={path} problems={problems}>
      {(describedBy) => (
        <div className="flex flex-col gap-1">
          <label htmlFor={id} className="font-medium">
            {label}
          </label>
          <select
            id={id}
            value={value}
            disabled={disabled}
            aria-describedby={describedBy}
            onChange={(e) => {
              const raw = e.target.value;
              const match = options.find((o) => String(o.value) === raw);
              onChange(match ? match.value : (raw as T));
            }}
            className={INPUT}
          >
            {options.map((o) => (
              <option key={String(o.value)} value={String(o.value)}>
                {o.text}
              </option>
            ))}
          </select>
        </div>
      )}
    </FieldShell>
  );
}

export function CheckControl({ path, label, checked, onChange, problems }: { path: string; label: string; checked: boolean; onChange: (checked: boolean) => void; problems: readonly EditProblem[] }) {
  const id = useId();
  return (
    <FieldShell path={path} problems={problems}>
      {(describedBy) => (
        <div className="flex items-center gap-2">
          <input id={id} type="checkbox" checked={checked} aria-describedby={describedBy} onChange={(e) => onChange(e.target.checked)} />
          <label htmlFor={id}>{label}</label>
        </div>
      )}
    </FieldShell>
  );
}

export function TextControl({
  path,
  label,
  value,
  onChange,
  problems,
  multiline,
}: {
  path: string;
  label: string;
  value: string;
  onChange: (value: string) => void;
  problems: readonly EditProblem[];
  multiline?: boolean;
}) {
  const id = useId();
  return (
    <FieldShell path={path} problems={problems}>
      {(describedBy) => (
        <div className="flex flex-col gap-1">
          <label htmlFor={id} className="font-medium">
            {label}
          </label>
          {multiline ? (
            <textarea id={id} value={value} rows={3} aria-describedby={describedBy} onChange={(e) => onChange(e.target.value)} className={INPUT} />
          ) : (
            <input id={id} type="text" value={value} aria-describedby={describedBy} onChange={(e) => onChange(e.target.value)} className={INPUT} />
          )}
        </div>
      )}
    </FieldShell>
  );
}

export function ReadOnly({ label, value, path, problems }: { label: string; value: ReactNode; path?: string; problems?: readonly EditProblem[] }) {
  const line = (
    <p>
      <span className="font-medium">{label}:</span> <span>{value}</span>
    </p>
  );
  if (!path || !problems) return line;
  // Not editable here, but a problem reported for it is still written beside it and the summary link lands on it.
  return (
    <FieldShell path={path} problems={problems}>
      {(describedBy) => (
        <div tabIndex={-1} aria-describedby={describedBy}>
          {line}
        </div>
      )}
    </FieldShell>
  );
}

/** A text box with a searchable list of the allowed values (a native datalist: typing filters it). */
export function ChoiceInput({
  path,
  label,
  value,
  choices,
  onChange,
  problems,
}: {
  path: string;
  label: string;
  value: string;
  choices: ReadonlyArray<{ value: string; text: string }>;
  onChange: (value: string) => void;
  problems: readonly EditProblem[];
}) {
  const id = useId();
  const listId = `${id}-list`;
  return (
    <FieldShell path={path} problems={problems}>
      {(describedBy) => (
        <div className="flex flex-col gap-1">
          <label htmlFor={id} className="font-medium">
            {label}
          </label>
          <input id={id} type="text" list={listId} value={value} autoComplete="off" aria-describedby={describedBy} onChange={(e) => onChange(e.target.value.trim())} className={INPUT} />
          <datalist id={listId}>
            {choices.map((c) => (
              <option key={c.value} value={c.value}>
                {c.text}
              </option>
            ))}
          </datalist>
        </div>
      )}
    </FieldShell>
  );
}
