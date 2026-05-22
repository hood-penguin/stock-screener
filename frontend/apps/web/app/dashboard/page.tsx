'use client'

import React from 'react'
import Link from 'next/link'
import { useQuery } from '@tanstack/react-query'
import { screenerApi } from '@/lib/api'
import { ScreeningResult } from '@/lib/types'

function StatCard({
  label,
  value,
  sub,
  color = 'text-primary',
}: {
  label: string
  value: string | number
  sub?: string
  color?: string
}) {
  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <p className="text-sm text-gray-500 mb-1">{label}</p>
      <p className={`text-3xl font-bold ${color}`}>{value}</p>
      {sub && <p className="text-xs text-gray-400 mt-1">{sub}</p>}
    </div>
  )
}

function TopStockRow({ result, rank }: { result: ScreeningResult; rank: number }) {
  const scoreColor =
    result.overall_score >= 70
      ? 'text-success'
      : result.overall_score >= 40
        ? 'text-warning'
        : 'text-danger'

  return (
    <Link href={`/screener/${result.ticker}`}>
      <div className="flex items-center gap-4 py-3 px-4 rounded-lg hover:bg-gray-50 transition cursor-pointer border-b last:border-0">
        <span className="text-gray-400 font-bold w-6 text-center">{rank}</span>
        <div className="flex-1">
          <span className="font-semibold text-gray-800">{result.ticker}</span>
          <span className="text-gray-500 text-sm ml-2">{result.company_name}</span>
        </div>
        <span className="bg-blue-100 text-blue-700 text-xs px-2 py-0.5 rounded">
          {result.market}
        </span>
        <span className={`font-bold text-lg w-14 text-right ${scoreColor}`}>
          {result.overall_score.toFixed(1)}
        </span>
      </div>
    </Link>
  )
}

export default function DashboardPage() {
  const { data: usData } = useQuery({
    queryKey: ['screener', 'US', 'dashboard'],
    queryFn: () => screenerApi.getResults({ market: 'US', page: 1, page_size: 200 }),
  })

  const { data: krData } = useQuery({
    queryKey: ['screener', 'KR', 'dashboard'],
    queryFn: () => screenerApi.getResults({ market: 'KR', page: 1, page_size: 200 }),
  })

  const usResults = usData?.data?.results ?? []
  const krResults = krData?.data?.results ?? []
  const allResults = [...usResults, ...krResults].sort(
    (a, b) => b.overall_score - a.overall_score
  )

  const usUndervalued = usResults.filter((r) => r.overall_score >= 60).length
  const krUndervalued = krResults.filter((r) => r.overall_score >= 60).length

  const usAvg =
    usResults.length > 0
      ? usResults.reduce((s, r) => s + r.overall_score, 0) / usResults.length
      : 0
  const krAvg =
    krResults.length > 0
      ? krResults.reduce((s, r) => s + r.overall_score, 0) / krResults.length
      : 0

  return (
    <div>
      <h1 className="text-4xl font-bold mb-8">대시보드</h1>

      {/* 통계 카드 */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        <StatCard
          label="미국 종목 수"
          value={usResults.length}
          sub={`저평가 후보 ${usUndervalued}개`}
          color="text-blue-600"
        />
        <StatCard
          label="한국 종목 수"
          value={krResults.length}
          sub={`저평가 후보 ${krUndervalued}개`}
          color="text-red-500"
        />
        <StatCard
          label="미국 평균 점수"
          value={usAvg.toFixed(1)}
          sub={`최고: ${usResults[0]?.overall_score.toFixed(1) ?? '-'}`}
          color="text-blue-600"
        />
        <StatCard
          label="한국 평균 점수"
          value={krAvg.toFixed(1)}
          sub={`최고: ${krResults[0]?.overall_score.toFixed(1) ?? '-'}`}
          color="text-red-500"
        />
      </div>

      {/* 상위 종목 */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* 전체 상위 10 */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-bold">전체 TOP 10</h2>
            <Link href="/screener" className="text-sm text-info hover:underline">
              전체 보기 →
            </Link>
          </div>
          {allResults.slice(0, 10).map((r, i) => (
            <TopStockRow key={r.id} result={r} rank={i + 1} />
          ))}
          {allResults.length === 0 && (
            <p className="text-gray-400 text-center py-8">데이터를 불러오는 중...</p>
          )}
        </div>

        {/* 마켓별 TOP 5 */}
        <div className="space-y-6">
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold">🇺🇸 미국 TOP 5</h2>
              <Link
                href="/screener?market=US"
                className="text-sm text-info hover:underline"
              >
                전체 보기 →
              </Link>
            </div>
            {usResults.slice(0, 5).map((r, i) => (
              <TopStockRow key={r.id} result={r} rank={i + 1} />
            ))}
            {usResults.length === 0 && (
              <p className="text-gray-400 text-center py-4">로딩 중...</p>
            )}
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold">🇰🇷 한국 TOP 5</h2>
              <Link
                href="/screener?market=KR"
                className="text-sm text-info hover:underline"
              >
                전체 보기 →
              </Link>
            </div>
            {krResults.slice(0, 5).map((r, i) => (
              <TopStockRow key={r.id} result={r} rank={i + 1} />
            ))}
            {krResults.length === 0 && (
              <p className="text-gray-400 text-center py-4">로딩 중...</p>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
