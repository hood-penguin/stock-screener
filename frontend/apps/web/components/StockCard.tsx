'use client'

import React from 'react'
import Link from 'next/link'
import { ScreeningResult } from '@/lib/types'

interface StockCardProps {
  result: ScreeningResult
}

export default function StockCard({ result }: StockCardProps) {
  const scorePercentage = (result.overall_score / 100) * 100

  return (
    <Link href={`/screener/${result.ticker}`}>
      <div className="bg-white rounded-lg shadow-md hover:shadow-lg transition p-6 cursor-pointer">
        {/* 헤더 */}
        <div className="flex items-start justify-between mb-4">
          <div>
            <h3 className="text-lg font-bold text-primary">{result.ticker}</h3>
            <p className="text-sm text-gray-600">{result.company_name}</p>
          </div>
          <div className="flex gap-2">
            <span className="bg-blue-100 text-blue-800 text-xs font-semibold px-2 py-1 rounded">
              {result.market}
            </span>
            <span className="bg-purple-100 text-purple-800 text-xs font-semibold px-2 py-1 rounded">
              {result.sector}
            </span>
          </div>
        </div>

        {/* 점수 프로그레스 바 */}
        <div className="mb-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-700">저평가 종합 점수</span>
            <span className="text-lg font-bold text-primary">
              {result.overall_score.toFixed(1)}
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-3">
            <div
              className="bg-gradient-to-r from-success to-info h-3 rounded-full transition-all"
              style={{ width: `${scorePercentage}%` }}
            ></div>
          </div>
        </div>

        {/* 메타정보 */}
        <div className="text-xs text-gray-500">
          평가일: {new Date(result.screened_at).toLocaleDateString('ko-KR')}
        </div>
      </div>
    </Link>
  )
}
