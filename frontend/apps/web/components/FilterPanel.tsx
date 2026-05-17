'use client'

import React from 'react'
import { useRouter, useSearchParams } from 'next/navigation'

interface FilterPanelProps {
  onFilterChange?: (filters: any) => void
}

export default function FilterPanel({ onFilterChange }: FilterPanelProps) {
  const router = useRouter()
  const searchParams = useSearchParams()

  const handleMarketChange = (market: string) => {
    const params = new URLSearchParams(searchParams)
    if (market === 'ALL') {
      params.delete('market')
    } else {
      params.set('market', market)
    }
    params.set('page', '1')
    router.push(`/screener?${params.toString()}`)
  }

  const handleSectorChange = (sector: string) => {
    const params = new URLSearchParams(searchParams)
    if (sector === '') {
      params.delete('sector')
    } else {
      params.set('sector', sector)
    }
    params.set('page', '1')
    router.push(`/screener?${params.toString()}`)
  }

  const handleScoreChange = (minScore: number) => {
    const params = new URLSearchParams(searchParams)
    if (minScore === 0) {
      params.delete('min_score')
    } else {
      params.set('min_score', minScore.toString())
    }
    params.set('page', '1')
    router.push(`/screener?${params.toString()}`)
  }

  const currentMarket = searchParams.get('market') || 'ALL'
  const currentSector = searchParams.get('sector') || ''
  const currentScore = Number(searchParams.get('min_score') || 0)

  return (
    <div className="bg-white rounded-lg shadow-md p-6 mb-6">
      <h2 className="text-lg font-semibold mb-4">필터</h2>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* 시장 필터 */}
        <div>
          <label className="block text-sm font-medium mb-2">시장</label>
          <div className="flex gap-2">
            {['ALL', 'US', 'KR'].map((market) => (
              <button
                key={market}
                onClick={() => handleMarketChange(market)}
                className={`px-4 py-2 rounded transition ${
                  currentMarket === market
                    ? 'bg-primary text-white'
                    : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                }`}
              >
                {market === 'ALL' ? '전체' : market}
              </button>
            ))}
          </div>
        </div>

        {/* 섹터 필터 */}
        <div>
          <label htmlFor="sector" className="block text-sm font-medium mb-2">
            섹터
          </label>
          <select
            id="sector"
            value={currentSector}
            onChange={(e) => handleSectorChange(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-primary"
          >
            <option value="">전체</option>
            <option value="Technology">기술</option>
            <option value="Healthcare">헬스케어</option>
            <option value="Finance">금융</option>
            <option value="Manufacturing">제조</option>
            <option value="Energy">에너지</option>
            <option value="Consumer">소비재</option>
          </select>
        </div>

        {/* 최소 점수 필터 */}
        <div>
          <label htmlFor="minScore" className="block text-sm font-medium mb-2">
            최소 점수: {currentScore}
          </label>
          <input
            id="minScore"
            type="range"
            min="0"
            max="100"
            step="5"
            value={currentScore}
            onChange={(e) => handleScoreChange(Number(e.target.value))}
            className="w-full"
          />
        </div>
      </div>
    </div>
  )
}
