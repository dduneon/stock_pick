import type { Recommendation } from '@/types';

async function getRecommendations(): Promise<Recommendation[]> {
  try {
    const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    const response = await fetch(`${baseUrl}/api/recommendations?limit=20`, {
      cache: 'no-store',
    });
    
    if (!response.ok) {
      console.error('Failed to fetch recommendations:', response.status);
      return [];
    }
    
    return response.json();
  } catch (error) {
    console.error('Error fetching recommendations:', error);
    return [];
  }
}

function formatPrice(price: number): string {
  return new Intl.NumberFormat('ko-KR', {
    style: 'currency',
    currency: 'KRW',
    maximumFractionDigits: 0,
  }).format(price);
}

function formatRatio(value: number | undefined): string {
  if (value === undefined || value === null) return '-';
  return value.toFixed(2);
}

export default async function Home() {
  const recommendations = await getRecommendations();

  return (
    <main className="min-h-screen bg-[#F9FAFB]">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <h1 className="text-xl font-bold text-gray-900">
            오늘의 추천 종목
          </h1>
          <p className="text-sm text-gray-500 mt-1">
            AI 기반 가치투자 추천 서비스
          </p>
        </div>
      </header>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {recommendations.length === 0 ? (
          <div className="text-center py-16">
            <p className="text-gray-500 text-lg">
              추천 종목을 불러오는 중입니다...
            </p>
            <p className="text-gray-400 text-sm mt-2">
              서버 연결을 확인해주세요
            </p>
          </div>
        ) : (
          <>
            {/* Stock Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
              {recommendations.map((stock) => {
                const isPositive = stock.change_rate >= 0;
                return (
                  <article
                    key={stock.ticker}
                    className="bg-white rounded-xl p-5 shadow-sm border border-gray-100 hover:shadow-md transition-shadow duration-200"
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
                          {formatRatio(stock.per)}배
                        </p>
                      </div>
                      <div>
                        <p className="text-xs text-gray-400 mb-1">PBR</p>
                        <p className="text-sm font-medium text-gray-900">
                          {formatRatio(stock.pbr)}배
                        </p>
                      </div>
                    </div>

                    {/* Recommendation Score */}
                    {stock.recommendation_score !== undefined && (
                      <div className="mt-3 pt-3 border-t border-gray-100">
                        <div className="flex items-center justify-between">
                          <p className="text-xs text-gray-400">종합점수</p>
                          <p className="text-sm font-semibold text-[#0045F6]">
                            {stock.recommendation_score.toFixed(1)}점
                          </p>
                        </div>
                        <div className="mt-1 h-1.5 bg-gray-100 rounded-full overflow-hidden">
                          <div
                            className="h-full bg-[#0045F6] rounded-full transition-all duration-500"
                            style={{
                              width: `${Math.min(stock.recommendation_score, 100)}%`,
                            }}
                          />
                        </div>
                      </div>
                    )}
                  </article>
                );
              })}
            </div>

            {/* Disclaimer Footer */}
            <footer className="mt-12 p-6 bg-gray-50 rounded-xl border border-gray-200">
              <h3 className="text-sm font-semibold text-gray-900 mb-2">
                ⚠️ 투자 고지사항
              </h3>
              <ul className="text-xs text-gray-500 space-y-1">
                <li>
                  • 본 서비스에서 제공하는 정보는仅供参考之用，不构成投资建议
                </li>
                <li>
                  • 과거 수익률이 미래 수익률을 보장하지 않습니다
                </li>
                <li>
                  • 투자 결정 전 반드시 본인의 투자 목표와 위험 감수를 확인하시기 바랍니다
                </li>
                <li>
                  • 본 서비스는 어떠한 손실에 대해서도 책임을 지지 않습니다
                </li>
              </ul>
            </footer>
          </>
        )}
      </div>
    </main>
  );
}
