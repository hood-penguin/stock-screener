'use client'

import React, { useEffect, useState } from 'react'
import { useSearchParams } from 'next/navigation'
import { useQuery } from '@tanstack/react-query'
import FilterPanel from '@/components/FilterPanel'
import StockCard from '@/components/StockCard'
import { screenerApi } from '@/lib/api'
import { ScreenerFilters } from '@/lib/types'

export default function ScreenerPage() {
  const searchParams = useSearchParams()
  const [filters, setFilters] = useState<ScreenerFilters>({})
  const [page, setPage] = useState(1)

  useEffect(() => {
    // URL 파라미터에서 필터 추출
    const market = searchParams.get('market')
    const sector = searchParams.get('sector')
    const minScore = searchParams.get('min_score')
    const pageParam = searchParams.get('page')

    setFilters({
      market: (market as any) || undefined,
      sector: sector || undefined,
      min_score: minScore ? Number(minScore) : undefined,
      page: pageParam ? Number(pageParam) : 1,
      page_size: 20,
    })

    setPage(pageParam ? Number(pageParam) : 1)
  }, [searchParams])

  const { data, isLoading, error } = useQuery({
    queryKey: ['screener', filters],
    queryFn: () => screenerApi.getResults(filters),
    enabled: Object.keys(filters).length > 0,
  })

  const results = data?.data

  return (
    <div>
      <h1 className="text-4xl font-bold mb-8">주식 스크리너</h1>

      <FilterPanel />

      {isLoading && (
        <div className="text-center py-12">
          <p className="text-gray-600">로딩 중...</p>
        </div>
      )}

      {error && (
        <div className="bg-danger text-white rounded-lg p-4 mb-6">
          데이터를 불러오는 중 오류가 발생했습니다.
        </div>
      )}

      {results && results.results.length > 0 && (
        <>
          <div className="mb-4">
            <p className="text-gray-600">
              총 {results.total}개 종목 중 {results.results.length}개 표시
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
            {results.results.map((result) => (
              <StockCard key={result.id} result={result} />
            ))}
          </div>

          {/* 페이지네이션 */}
          {results.total_pages > 1 && (
            <div className="flex items-center justify-center gap-2 mt-8">
              <button
                onClick={() => setPage(Math.max(1, page - 1))}
                disabled={page === 1}
                className="px-4 py-2 bg-gray-200 rounded disabled:opacity-50"
              >
                이전
              </button>

              {Array.from({ length: results.total_pages }, (_, i) => i + 1).map((p) => (
                <button
                  key={p}
                  onClick={() => setPage(p)}
                  className={`px-4 py-2 rounded ${
                    page === p
                      ? 'bg-primary text-white'
                      : 'bg-gray-200 hover:bg-gray-300'
                  }`}
                >
                  {p}
                </button>
              ))}

              <button
                onClick={() => setPage(Math.min(results.total_pages, page + 1))}
                disabled={page === results.total_pages}
                className="px-4 py-2 bg-gray-200 rounded disabled:opacity-50"
              >
                다음
              </button>
            </div>
          )}
        </>
      )}

      {results && results.results.length === 0 && (
        <div className="text-center py-12">
          <p className="text-gray-600">조건에 맞는 종목이 없습니다.</p>
        </div>
      )}
    </div>
  )
}
