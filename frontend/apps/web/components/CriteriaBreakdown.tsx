'use client'

import React from 'react'
import { CriteriaScore } from '@/lib/types'

interface CriteriaBreakdownProps {
  criteria: CriteriaScore[]
}

const CRITERIA_CATEGORIES = {
  valuation: ['PE Ratio', 'PB Ratio', 'PS Ratio', 'PEG Ratio', 'EV/EBITDA'],
  profitability: ['ROE', 'ROA', 'Net Margin', 'Gross Margin', 'Operating Margin'],
  growth: ['Revenue Growth', 'EPS Growth'],
  financial_health: ['Debt to Equity', 'Current Ratio', 'Quick Ratio', 'Interest Coverage'],
}

export default function CriteriaBreakdown({ criteria }: CriteriaBreakdownProps) {
  const categorized = {
    valuation: criteria.filter((c) =>
      CRITERIA_CATEGORIES.valuation.some((cat) => c.criterion_name.includes(cat))
    ),
    profitability: criteria.filter((c) =>
      CRITERIA_CATEGORIES.profitability.some((cat) => c.criterion_name.includes(cat))
    ),
    growth: criteria.filter((c) =>
      CRITERIA_CATEGORIES.growth.some((cat) => c.criterion_name.includes(cat))
    ),
    financial_health: criteria.filter((c) =>
      CRITERIA_CATEGORIES.financial_health.some((cat) => c.criterion_name.includes(cat))
    ),
  }

  const renderCategory = (title: string, items: CriteriaScore[]) => {
    if (items.length === 0) return null

    return (
      <div key={title} className="mb-6">
        <h3 className="text-lg font-semibold text-primary mb-4">{title}</h3>
        <div className="space-y-3">
          {items.map((item) => (
            <div
              key={item.id}
              className="bg-gray-50 rounded-lg p-4 border-l-4 border-info"
            >
              <div className="flex items-start justify-between mb-2">
                <span className="font-medium text-gray-800">
                  {item.criterion_name}
                </span>
                {item.score !== null && (
                  <span
                    className={`font-bold px-3 py-1 rounded ${
                      item.score >= 70
                        ? 'bg-success text-white'
                        : item.score >= 40
                          ? 'bg-warning text-white'
                          : 'bg-danger text-white'
                    }`}
                  >
                    {item.score.toFixed(1)}
                  </span>
                )}
              </div>
              {item.reason && (
                <p className="text-sm text-gray-600">{item.reason}</p>
              )}
            </div>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-2xl font-bold mb-6">기준별 분석</h2>

      {renderCategory('저평가 지표', categorized.valuation)}
      {renderCategory('수익성 지표', categorized.profitability)}
      {renderCategory('성장성 지표', categorized.growth)}
      {renderCategory('재무 건강도', categorized.financial_health)}

      {criteria.length === 0 && (
        <p className="text-gray-500 text-center py-8">
          평가 기준 정보가 없습니다.
        </p>
      )}
    </div>
  )
}
