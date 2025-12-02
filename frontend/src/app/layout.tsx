import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Real-Time Transcription',
  description: 'CPU-based real-time speech-to-text service using Vosk',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}