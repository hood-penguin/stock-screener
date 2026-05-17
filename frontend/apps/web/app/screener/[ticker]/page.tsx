'use client'

import React, { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import Link from 'next/link'
import { screenerApi } from '@/lib/api'
import ScoreGauge from '@/components/ScoreGauge'
import CriteriaBreakdown from '@/components/CriteriaBreakdown'

interface PageProps {
  params: Promise<{ ticker: string }>
}

export default function StockDetailPage({ params }: PageProps) {
  const { ticker } = React.use(params)
  const [isWatchlisted, setIsWatchlisted] = useState(false)

  const { data, isLoading, error } = useQuery({
    queryKey: ['stock-detail', ticker],
    queryFn: () => screenerApi.getResultByTicker(ticker),
  })

  const result = data?.data

  if (isLoading) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-600">로딩 중...</p>
      </div>
    )
  }

  if (error || !result) {
    return (
      <div className="text-center py-12">
        <p className="text-danger">종목 정보를 불러올 수 없습니다.</p>
        <Link href="/screener" className="text-info hover:underline mt-4 inline-block">
          스크리너로 돌아가기
        </Link>
      </div>
    )
  }

  return (
    <div>
      {/* 헤더 */}
      <div className="mb-8">
        <Link href="/screener" className="text-info hover:underline mb-4 inline-block">
          &larr; 스크리너로 돌아가기
        </Link>

        <div className="bg-white rounded-lg shadow-md p-8">
          <div className="flex items-start justify-between mb-6">
            <div>
              <h1 className="text-4xl font-bold text-primary mb-2">{result.ticker}</h1>
              <p className="text-xl text-gray-600">{result.company_name}</p>
              <div className="flex gap-3 mt-4">
                <span className="bg-blue-100 text-blue-800 text-sm font-semibold px-3 py-1 rounded">
                  {result.market}
                </span>
                <span className="bg-purple-100 text-purple-800 text-sm font-semibold px-3 py-1 rounded">
                  {result.sector}
                </span>
              </div>
            </div>

            <div className="text-right">
              <button
                onClick={() => setIsWatchlisted(!isWatchlisted)}
                className={`px-6 py-2 rounded font-medium transition ${
                  isWatchlisted
                    ? 'bg-danger text-white'
                    : 'bg-info text-white hover:opacity-90'
                }`}
              >
                {isWatchlisted ? '관심 종목 제거' : '관심 종목 추가'}
              </button>
            </div>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-gray-50 p-4 rounded">
              <p className="text-gray-600 text-sm">평가일</p>
              <p className="text-lg font-semibold">
                {new Date(result.screened_at).toLocaleDateString('ko-KR')}
              </p>
            </div>
            <div className="bg-gray-50 p-4 rounded">
              <p className="text-gray-600 text-sm">저평가 점수</p>
              <p className="text-lg font-semibold">{result.overall_score.toFixed(1)}</p>
            </div>
          </div>
        </div>
      </div>

      {/* 저평가 점수 게이지 */}
      <div className="bg-white rounded-lg shadow-md p-8 mb-8">
        <h2 className="text-2xl font-bold mb-8 text-center">저평가 종합 평가</h2>
        <div className="flex justify-center">
          <ScoreGauge score={result.overall_score} />
        </div>
      </div>

      {/* 기준별 분석 */}
      <CriteriaBreakdown criteria={result.criteria_scores} />
    </div>
  )
}
