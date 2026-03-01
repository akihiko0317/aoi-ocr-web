"use client";

import { useState } from "react";
import ImageUploader from "@/components/ImageUploader";
import OcrResult from "@/components/OcrResult";
// TODO: Add a history sidebar that shows previously processed images and their results
// TODO: Add support for drag-and-drop of multiple images for batch processing

export default function Home() {
  const [extractedText, setExtractedText] = useState<string>("");
  const [isProcessing, setIsProcessing] = useState(false);

  const handleImageSelect = async (file: File) => {
    setIsProcessing(true);
    setExtractedText("");

    // TODO: Replace this mock OCR with actual Tesseract.js integration
    // For now, simulate OCR processing with a delay
    await new Promise((resolve) => setTimeout(resolve, 1500));
    setExtractedText(
      `[Mock OCR Result]\n\nText extracted from: ${file.name}\nFile size: ${(file.size / 1024).toFixed(1)} KB\nFile type: ${file.type}\n\nTo enable real OCR, integrate Tesseract.js in this handler.`
    );
    setIsProcessing(false);
  };

  return (
    <div className="flex min-h-screen flex-col bg-zinc-50 dark:bg-zinc-950">
      <header className="border-b border-zinc-200 bg-white px-6 py-4 dark:border-zinc-800 dark:bg-zinc-900">
        <div className="mx-auto max-w-4xl">
          <h1 className="text-2xl font-bold text-zinc-900 dark:text-zinc-100">
            Aoi OCR
          </h1>
          <p className="text-sm text-zinc-500 dark:text-zinc-400">
            Extract text from images using optical character recognition
          </p>
        </div>
      </header>

      <main className="mx-auto w-full max-w-4xl flex-1 px-6 py-8">
        <div className="grid gap-8 md:grid-cols-2">
          <section>
            <h2 className="mb-4 text-lg font-semibold text-zinc-800 dark:text-zinc-200">
              Upload Image
            </h2>
            <ImageUploader
              onImageSelect={handleImageSelect}
              isProcessing={isProcessing}
            />
          </section>

          <section>
            <h2 className="mb-4 text-lg font-semibold text-zinc-800 dark:text-zinc-200">
              Extracted Text
            </h2>
            <OcrResult text={extractedText} isProcessing={isProcessing} />
          </section>
        </div>
      </main>

      {/* TODO: Add a footer with links to documentation and GitHub repository */}
    </div>
  );
}
