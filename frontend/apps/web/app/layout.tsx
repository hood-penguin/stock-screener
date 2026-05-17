'use client'

import React from 'react'
import Link from 'next/link'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import './globals.css'

const queryClient = new QueryClient()

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="ko">
      <head>
        <title>Stock Screener</title>
        <meta name="description" content="저평가 주식 자동 탐색 서비스" />
      </head>
      <body>
        <QueryClientProvider client={queryClient}>
          <nav className="bg-primary text-white shadow-md">
            <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
              <Link href="/" className="text-xl font-bold">
                Stock Screener
              </Link>
              <ul className="flex gap-6">
                <li>
                  <Link href="/screener" className="hover:text-gray-300 transition">
                    스크리너
                  </Link>
                </li>
                <li>
                  <Link href="/watchlist" className="hover:text-gray-300 transition">
                    관심 종목
                  </Link>
                </li>
                <li>
                  <Link href="/dashboard" className="hover:text-gray-300 transition">
                    대시보드
                  </Link>
                </li>
              </ul>
            </div>
          </nav>
          <main className="max-w-7xl mx-auto px-4 py-8">
            {children}
          </main>
        </QueryClientProvider>
      </body>
    </html>
  )
}
