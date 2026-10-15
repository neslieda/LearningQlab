import type { Metadata } from "next";
import { Gallery } from "./gallery";

export const metadata: Metadata = { title: "Renderer gallery" };

// Synthetic fixtures only; no API calls. Available in production builds (visual regression target).
export default function GalleryPage() {
  return <Gallery />;
}
