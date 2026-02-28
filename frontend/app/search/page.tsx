'use client';

import { useState, useEffect, Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { Search, Loader2, TrendingUp, TrendingDown } from 'lucide-react';
import type { StockDetail } from '@/types';
import Header from '@/components/Header';
import EmptyState from '@/components/EmptyState';

function SearchResultsContent() {
  const searchParams = useSearchParams();
  const query = searchParams.get('q') || '';
  
  const [results, setResults] = useState<StockDetail[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!query.trim()) {
      setResults([]);
      return;
    }

    async function fetchResults() {
      setLoading(true);
      setError(null);

      try {
        const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
        const response = await fetch(
          `${baseUrl}/api/search?q=${encodeURIComponent(query)}`,
          { cache: 'no-store' }
        );

        if (!response.ok) {
          throw new Error('Failed to fetch search results');
        }

        const data: StockDetail[] = await response.json();
        setResults(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error');
        setResults([]);
      } finally {
        setLoading(false);
      }
    }

    fetchResults();
  }, [query]);

  const formatPrice = (price: number): string => {
    return new Intl.NumberFormat('ko-KR', {
      style: 'currency',
      currency: 'KRW',
      maximumFractionDigits: 0,
    }).format(price);
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Search Info */}
      <div className="mb-6">
        <h1 className="text-xl font-bold text-gray-900">
          검색 결과
        </h1>
        <p className="text-sm text-gray-500 mt-1">
          &quot;<span className="font-medium text-gray-900">{query}</span>&quot; 검색 결과
          {loading ? (
            <span className="ml-2">검색 중...</span>
          ) : (
            <span className="ml-2">{results.length}개 종목</span>
          )}
        </p>
      </div>

      {/* Loading State */}
      {loading && (
        <div className="flex flex-col items-center justify-center py-16">
          <Loader2 className="w-8 h-8 text-[#0045F6] animate-spin" />
          <p className="text-gray-500 mt-4">검색 중...</p>
        </div>
      )}

      {/* Error State */}
      {!loading && error && (
        <EmptyState
          variant="error"
          title="검색 중 오류가 발생했습니다"
          description={error}
        />
      )}

      {/* Empty State */}
      {!loading && !error && results.length === 0 && (
        <EmptyState
          variant="search"
          title="검색 결과가 없습니다"
          description="다른 검색어를 입력핫세요"
        />
      )}

      {/* Results Grid */}
      {!loading && !error && results.length > 0 && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {results.map((stock) => {
            const isPositive = stock.change_rate >= 0;
            return (
              <Link
                key={stock.ticker}
                href={`/stocks/${stock.ticker}`}
                className="bg-white rounded-xl p-5 shadow-sm border border-gray-100 
                           hover:shadow-md hover:border-[#0045F6]/20 transition-all duration-200"
              >
                {/* Header */}
                <div className="flex items-start justify-between mb-3">
                  <div className="flex-1 min-w-0">
                    <h2 className="text-lg font-semibold text-gray-900 truncate">
                      {stock.ticker}
                    </h2>
                    <p className="text-sm text-gray-500 truncate">
                      {stock.name}
                    </p>
                  </div>
                  <div
                    className={`flex items-center px-2 py-1 rounded-md text-sm font-medium ${
                      isPositive
                        ? 'bg-[#E5493A]/10 text-[#E5493A]'
                        : 'bg-[#2972FF]/10 text-[#2972FF]'
                    }`}
                  >
                    <span className="mr-1">
                      {isPositive ? '▲' : '▼'}
                    </span>
                    {Math.abs(stock.change_rate).toFixed(2)}%
                  </div>
                </div>

                {/* Current Price */}
                <div className="mb-4">
                  <p className="text-2xl font-bold text-gray-900">
                    {formatPrice(stock.current_price)}
                  </p>
                </div>

                {/* Metrics */}
                <div className="grid grid-cols-2 gap-3 pt-3 border-t border-gray-100">
                  <div>
                    <p className="text-xs text-gray-400 mb-1">PER</p>
                    <p className="text-sm font-medium text-gray-900">
                      {stock.per !== undefined ? `${stock.per.toFixed(2)}배` : '-'}
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-400 mb-1">PBR</p>
                    <p className="text-sm font-medium text-gray-900">
                      {stock.pbr !== undefined ? `${stock.pbr.toFixed(2)}배` : '-'}
                    </p>
                  </div>
                </div>
              </Link>
            );
          })}
        </div>
      )}
    </div>
  );
}

function SearchResultsLoading() {
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="flex flex-col items-center justify-center py-16">
        <Loader2 className="w-8 h-8 text-[#0045F6] animate-spin" />
        <p className="text-gray-500 mt-4">로딩 중...</p>
      </div>
    </div>
  );
}

export default function SearchPage() {
  return (
    <main className="min-h-screen bg-[#F9FAFB]">
      <Header />

      {/* Page Title */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <h1 className="text-xl font-bold text-gray-900">종목 검색</h1>
          <p className="text-sm text-gray-500">원하는 종목을 검색핫세요</p>
        </div>
      </div>

      {/* Search Results */}
      <Suspense fallback={<SearchResultsLoading />}>
        <SearchResultsContent />
      </Suspense>
    </main>
  );
}
