'use client'

import React, { useEffect, useState } from 'react'
import Link from 'next/link'
import { useQuery } from '@tanstack/react-query'
import { screenerApi } from '@/lib/api'
import { getWatchlist, removeFromWatchlist } from '@/lib/watchlist'
import { ScreeningResult } from '@/lib/types'

function WatchlistCard({
  ticker,
  onRemove,
}: {
  ticker: string
  onRemove: (t: string) => void
}) {
  const { data, isLoading, error } = useQuery({
    queryKey: ['stock-detail', ticker],
    queryFn: () => screenerApi.getResultByTicker(ticker),
    retry: false,
  })

  const result = data?.data as (ScreeningResult & { overall_score: number }) | undefined

  if (isLoading) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6 animate-pulse">
        <div className="h-4 bg-gray-200 rounded w-24 mb-2" />
        <div className="h-3 bg-gray-100 rounded w-40" />
      </div>
    )
  }

  if (error || !result) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6 border-l-4 border-danger">
        <div className="flex items-center justify-between">
          <div>
            <p className="font-bold text-gray-800">{ticker}</p>
            <p className="text-sm text-danger">정보를 불러올 수 없습니다.</p>
          </div>
          <button
            onClick={() => onRemove(ticker)}
            className="text-gray-400 hover:text-danger transition text-sm"
          >
            제거
          </button>
        </div>
      </div>
    )
  }

  const scoreColor =
    result.overall_score >= 70
      ? 'text-success'
      : result.overall_score >= 40
        ? 'text-warning'
        : 'text-danger'

  const barColor =
    result.overall_score >= 70
      ? 'bg-success'
      : result.overall_score >= 40
        ? 'bg-warning'
        : 'bg-danger'

  return (
    <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition">
      <div className="flex items-start justify-between mb-4">
        <Link href={`/screener/${result.ticker}`} className="flex-1">
          <h3 className="text-lg font-bold text-primary">{result.ticker}</h3>
          <p className="text-sm text-gray-500">{result.company_name}</p>
          <div className="flex gap-2 mt-2">
            <span className="bg-blue-100 text-blue-700 text-xs px-2 py-0.5 rounded">
              {result.market}
            </span>
            {result.sector && (
              <span className="bg-purple-100 text-purple-700 text-xs px-2 py-0.5 rounded">
                {result.sector}
              </span>
            )}
          </div>
        </Link>
        <button
          onClick={() => onRemove(ticker)}
          className="text-gray-300 hover:text-danger transition ml-2 text-xl leading-none"
          title="관심 종목 제거"
        >
          ×
        </button>
      </div>

      <div className="mb-2 flex items-center justify-between">
        <span className="text-sm text-gray-500">저평가 점수</span>
        <span className={`font-bold text-lg ${scoreColor}`}>
          {result.overall_score.toFixed(1)}
        </span>
      </div>
      <div className="w-full bg-gray-200 rounded-full h-2">
        <div
          className={`${barColor} h-2 rounded-full transition-all`}
          style={{ width: `${Math.min(100, result.overall_score)}%` }}
        />
      </div>
    </div>
  )
}

export default function WatchlistPage() {
  const [tickers, setTickers] = useState<string[]>([])
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setTickers(getWatchlist())
    setMounted(true)
  }, [])

  const handleRemove = (ticker: string) => {
    removeFromWatchlist(ticker)
    setTickers(getWatchlist())
  }

  if (!mounted) return null

  return (
    <div>
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-4xl font-bold">관심 종목</h1>
        {tickers.length > 0 && (
          <span className="text-gray-500 text-sm">{tickers.length}개 종목</span>
        )}
      </div>

      {tickers.length === 0 ? (
        <div className="text-center py-20">
          <p className="text-gray-400 text-lg mb-4">관심 종목이 없습니다.</p>
          <Link
            href="/screener"
            className="bg-primary text-white px-6 py-3 rounded-lg hover:opacity-90 transition"
          >
            스크리너에서 종목 추가하기
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {tickers.map((ticker) => (
            <WatchlistCard key={ticker} ticker={ticker} onRemove={handleRemove} />
          ))}
        </div>
      )}
    </div>
  )
}
