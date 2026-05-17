'use client'

import React from 'react'

interface ScoreGaugeProps {
  score: number
  maxScore?: number
}

export default function ScoreGauge({ score, maxScore = 100 }: ScoreGaugeProps) {
  const percentage = (score / maxScore) * 100

  // 점수에 따른 색상 결정
  let color = '#ef4444' // red (0-33)
  if (percentage >= 33 && percentage < 67) {
    color = '#f59e0b' // amber (33-67)
  } else if (percentage >= 67) {
    color = '#10b981' // green (67-100)
  }

  return (
    <div className="flex flex-col items-center">
      <div className="relative w-32 h-32">
        {/* 백그라운드 원 */}
        <svg
          className="w-full h-full transform -rotate-90"
          viewBox="0 0 120 120"
        >
          {/* 배경 */}
          <circle
            cx="60"
            cy="60"
            r="50"
            stroke="#e5e7eb"
            strokeWidth="8"
            fill="none"
          />
          {/* 진행도 */}
          <circle
            cx="60"
            cy="60"
            r="50"
            stroke={color}
            strokeWidth="8"
            fill="none"
            strokeDasharray={`${percentage * 3.14} 314`}
            strokeLinecap="round"
            className="transition-all duration-500"
          />
        </svg>

        {/* 중앙 텍스트 */}
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-3xl font-bold" style={{ color }}>
            {score.toFixed(1)}
          </span>
          <span className="text-xs text-gray-600">/ {maxScore}</span>
        </div>
      </div>

      {/* 라벨 */}
      <div className="mt-4 text-center">
        {percentage < 33 && <p className="text-danger font-medium">고평가</p>}
        {percentage >= 33 && percentage < 67 && (
          <p className="text-warning font-medium">보통</p>
        )}
        {percentage >= 67 && <p className="text-success font-medium">저평가</p>}
      </div>
    </div>
  )
}
