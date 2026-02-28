'use client';

import { useState, useEffect, useMemo, useCallback } from 'react';
import { 
  ArrowUpDown, 
  ArrowUp, 
  ArrowDown, 
  ChevronLeft, 
  ChevronRight,
  X,
  ChevronDown,
  ChevronUp,
  Info
} from 'lucide-react';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';
import Header from '@/components/Header';
import EmptyState from '@/components/EmptyState';

/** Utility for merging tailwind classes */
function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

/** Stock data type from API */
interface Stock {
  ticker: string;
  name: string;
  current_price: number;
  change_rate: number;
  per?: number;
  pbr?: number;
  market_cap?: number;
  eps?: number;
  bps?: number;
  // New fields (from Wave 1)
  forward_pe?: number;
  roe?: number;
  debt_ratio?: number;
  eps_growth_yoy?: number;
  sector?: string;
  // New fields (from Wave 2)
  rsi_14?: number;
  ma_5?: number;
  ma_20?: number;
  trend?: 'uptrend' | 'downtrend' | 'sideways';
  volume_spike?: boolean;
  // Calculated
  recommendation_score?: number;
}

/** Sort field types */
type SortField = 'market_cap' | 'per' | 'pbr' | 'change_rate' | 'roe' | 'debt_ratio' | 'forward_pe' | 'recommendation_score';
type SortDirection = 'asc' | 'desc';

/** RSI range filter */
type RsiRange = 'oversold' | 'neutral' | 'overbought' | 'all';

/** Filter state */
interface FilterState {
  // Existing
  perMin: string;
  perMax: string;
  marketCapMin: string;
  // New filters
  pbrMin: string;
  pbrMax: string;
  roeMin: string;
  debtRatioMax: string;
  forwardPeMax: string;
  rsiRange: RsiRange;
  volumeSpike: boolean;
}

/** Sort option definition */
const sortOptions: { field: SortField; label: string }[] = [
  { field: 'market_cap', label: '시가총액' },
  { field: 'per', label: 'PER' },
  { field: 'pbr', label: 'PBR' },
  { field: 'change_rate', label: '등락률' },
  { field: 'roe', label: 'ROE ↑' },
  { field: 'debt_ratio', label: '부채비율 ↓' },
  { field: 'forward_pe', label: 'Forward P/E' },
  { field: 'recommendation_score', label: '추천점수' },
];

/** Technical signal labels */
const technicalSignalLabels: Record<string, { label: string; variant: string }> = {
  oversold: { label: '과매도', variant: 'blue' },
  uptrend: { label: '상승추세', variant: 'green' },
  downtrend: { label: '하락추세', variant: 'red' },
  overbought: { label: '과매수', variant: 'orange' },
  neutral: { label: '중립', variant: 'gray' },
  sideways: { label: '보합', variant: 'gray' },
};

const ITEMS_PER_PAGE = 20;

export default function StocksPage() {
  const [stocks, setStocks] = useState<Stock[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Sort state
  const [sortField, setSortField] = useState<SortField>('market_cap');
  const [sortDirection, setSortDirection] = useState<SortDirection>('desc');
  
  // Filter state
  const [filters, setFilters] = useState<FilterState>({
    perMin: '',
    perMax: '',
    marketCapMin: '',
    pbrMin: '',
    pbrMax: '',
    roeMin: '',
    debtRatioMax: '',
    forwardPeMax: '',
    rsiRange: 'all',
    volumeSpike: false,
  });
  
  // Filter panel collapse state
  const [showAdvancedFilters, setShowAdvancedFilters] = useState(false);
  
  // Pagination state
  const [currentPage, setCurrentPage] = useState(1);
  
  // Fetch stocks data
  useEffect(() => {
    async function fetchStocks() {
      try {
        const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
        const response = await fetch(`${baseUrl}/api/stocks`, {
          cache: 'no-store',
        });
        
        if (!response.ok) {
          throw new Error('Failed to fetch stocks');
        }
        
        const data = await response.json();
        setStocks(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error');
      } finally {
        setLoading(false);
      }
    }
    
    fetchStocks();
  }, []);
  
  // Handle filter change
  const handleFilterChange = useCallback((field: keyof FilterState, value: string | boolean) => {
    setFilters(prev => ({ ...prev, [field]: value }));
    setCurrentPage(1);
  }, []);
  
  // Clear filters
  const clearFilters = useCallback(() => {
    setFilters({
      perMin: '',
      perMax: '',
      marketCapMin: '',
      pbrMin: '',
      pbrMax: '',
      roeMin: '',
      debtRatioMax: '',
      forwardPeMax: '',
      rsiRange: 'all',
      volumeSpike: false,
    });
    setCurrentPage(1);
  }, []);
  
  // Handle sort
  const handleSort = useCallback((field: SortField) => {
    if (sortField === field) {
      setSortDirection(prev => prev === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      // Default to descending for most fields, ascending for debt_ratio
      setSortDirection(field === 'debt_ratio' ? 'asc' : 'desc');
    }
    setCurrentPage(1);
  }, [sortField]);
  
  // Determine technical signal based on RSI and trend
  const getTechnicalSignal = useCallback((stock: Stock): string => {
    if (stock.rsi_14 !== undefined) {
      if (stock.rsi_14 < 30) return 'oversold';
      if (stock.rsi_14 > 70) return 'overbought';
    }
    if (stock.trend === 'uptrend') return 'uptrend';
    if (stock.trend === 'downtrend') return 'downtrend';
    return 'neutral';
  }, []);
  
  // Filter and sort stocks
  const filteredAndSortedStocks = useMemo(() => {
    let result = [...stocks];
    
    // Apply PER filter
    if (filters.perMin) {
      const min = parseFloat(filters.perMin);
      if (!isNaN(min)) {
        result = result.filter(stock => stock.per !== undefined && stock.per >= min);
      }
    }
    
    if (filters.perMax) {
      const max = parseFloat(filters.perMax);
      if (!isNaN(max)) {
        result = result.filter(stock => stock.per !== undefined && stock.per <= max);
      }
    }
    
    // Apply Market Cap filter
    if (filters.marketCapMin) {
      const min = parseFloat(filters.marketCapMin) * 1_000_000_000;
      if (!isNaN(min)) {
        result = result.filter(stock => stock.market_cap !== undefined && stock.market_cap >= min);
      }
    }
    
    // Apply PBR filter
    if (filters.pbrMin) {
      const min = parseFloat(filters.pbrMin);
      if (!isNaN(min)) {
        result = result.filter(stock => stock.pbr !== undefined && stock.pbr >= min);
      }
    }
    
    if (filters.pbrMax) {
      const max = parseFloat(filters.pbrMax);
      if (!isNaN(max)) {
        result = result.filter(stock => stock.pbr !== undefined && stock.pbr <= max);
      }
    }
    
    // Apply ROE filter
    if (filters.roeMin) {
      const min = parseFloat(filters.roeMin);
      if (!isNaN(min)) {
        result = result.filter(stock => stock.roe !== undefined && stock.roe >= min);
      }
    }
    
    // Apply Debt Ratio filter
    if (filters.debtRatioMax) {
      const max = parseFloat(filters.debtRatioMax);
      if (!isNaN(max)) {
        result = result.filter(stock => stock.debt_ratio !== undefined && stock.debt_ratio <= max);
      }
    }
    
    // Apply Forward P/E filter
    if (filters.forwardPeMax) {
      const max = parseFloat(filters.forwardPeMax);
      if (!isNaN(max)) {
        result = result.filter(stock => stock.forward_pe !== undefined && stock.forward_pe <= max);
      }
    }
    
    // Apply RSI filter
    if (filters.rsiRange !== 'all') {
      result = result.filter(stock => {
        if (stock.rsi_14 === undefined) return false;
        switch (filters.rsiRange) {
          case 'oversold':
            return stock.rsi_14 < 30;
          case 'overbought':
            return stock.rsi_14 > 70;
          case 'neutral':
            return stock.rsi_14 >= 30 && stock.rsi_14 <= 70;
          default:
            return true;
        }
      });
    }
    
    // Apply Volume Spike filter
    if (filters.volumeSpike) {
      result = result.filter(stock => stock.volume_spike === true);
    }
    
    // Apply sorting
    result.sort((a, b) => {
      let aVal: number | undefined;
      let bVal: number | undefined;
      
      switch (sortField) {
        case 'market_cap':
          aVal = a.market_cap;
          bVal = b.market_cap;
          break;
        case 'per':
          aVal = a.per;
          bVal = b.per;
          break;
        case 'pbr':
          aVal = a.pbr;
          bVal = b.pbr;
          break;
        case 'change_rate':
          aVal = a.change_rate;
          bVal = b.change_rate;
          break;
        case 'roe':
          aVal = a.roe;
          bVal = b.roe;
          break;
        case 'debt_ratio':
          aVal = a.debt_ratio;
          bVal = b.debt_ratio;
          break;
        case 'forward_pe':
          aVal = a.forward_pe;
          bVal = b.forward_pe;
          break;
        case 'recommendation_score':
          aVal = a.recommendation_score;
          bVal = b.recommendation_score;
          break;
      }
      
      // Handle undefined values - push to end
      if (aVal === undefined && bVal === undefined) return 0;
      if (aVal === undefined) return 1;
      if (bVal === undefined) return -1;
      
      const diff = aVal - bVal;
      return sortDirection === 'asc' ? diff : -diff;
    });
    
    return result;
  }, [stocks, filters, sortField, sortDirection]);

  const paginatedStocks = useMemo(() => {
    const start = (currentPage - 1) * ITEMS_PER_PAGE;
    return filteredAndSortedStocks.slice(start, start + ITEMS_PER_PAGE);
  }, [filteredAndSortedStocks, currentPage]);

  const totalPages = Math.ceil(filteredAndSortedStocks.length / ITEMS_PER_PAGE);
  
  // Format helpers
  const formatMarketCap = (value: number | undefined): string => {
    if (value === undefined || value === null) return '-';
    if (value >= 1_000_000_000_000) {
      return `${(value / 1_000_000_000_000).toFixed(2)}조`;
    }
    return `${(value / 1_000_000_000).toFixed(0)}억`;
  };
  
  const formatRatio = (value: number | undefined): string => {
    if (value === undefined || value === null) return '-';
    return value.toFixed(2);
  };

  const formatPercent = (value: number | undefined): string => {
    if (value === undefined || value === null) return '-';
    return `${value.toFixed(1)}%`;
  };


  const formatPrice = (value: number | undefined): string => {
    if (value === undefined || value === null) return '-';
    return value.toLocaleString('ko-KR');
  };
  
  // Check for active filters
  const hasActiveFilters = 
    filters.perMin || filters.perMax || filters.marketCapMin ||
    filters.pbrMin || filters.pbrMax || filters.roeMin ||
    filters.debtRatioMax || filters.forwardPeMax ||
    filters.rsiRange !== 'all' || filters.volumeSpike;
  
  // Sort icon component
  const SortIcon = ({ field }: { field: SortField }) => {
    if (sortField !== field) {
      return <ArrowUpDown className="w-4 h-4 text-gray-400" />;
    }
    return sortDirection === 'asc' 
      ? <ArrowUp className="w-4 h-4 text-[#0045F6]" />
      : <ArrowDown className="w-4 h-4 text-[#0045F6]" />;
  };
  
  // Badge component for technical signals
  const TechnicalBadge = ({ signal }: { signal: string }) => {
    const config = technicalSignalLabels[signal] || technicalSignalLabels.neutral;
    const variantClasses: Record<string, string> = {
      blue: 'bg-blue-100 text-blue-700',
      green: 'bg-green-100 text-green-700',
      red: 'bg-red-100 text-red-700',
      orange: 'bg-orange-100 text-orange-700',
      gray: 'bg-gray-100 text-gray-700',
    };
    
    return (
      <span className={cn("inline-flex items-center px-2 py-0.5 rounded text-xs font-medium", variantClasses[config.variant])}>
        {config.label}
      </span>
    );
  };
  
  // Tooltip component
  const Tooltip = ({ text }: { text: string }) => (
    <div className="group relative inline-block ml-1">
      <Info className="w-3.5 h-3.5 text-gray-400 cursor-help" />
      <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 px-2 py-1 bg-gray-900 text-white text-xs rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap z-10">
        {text}
      </div>
    </div>
  );
  
  if (loading) {
    return (
      <main className="min-h-screen bg-[#F9FAFB]">
        <header className="bg-white border-b border-gray-200 sticky top-0 z-10">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
            <h1 className="text-xl font-bold text-gray-900">전종목 리스트</h1>
            <p className="text-sm text-gray-500 mt-1">국내上市 전체 종목</p>
          </div>
        </header>
        <div className="flex items-center justify-center h-[calc(100vh-80px)]">
          <div className="flex flex-col items-center gap-3">
            <div className="w-8 h-8 border-4 border-[#0045F6] border-t-transparent rounded-full animate-spin" />
            <p className="text-gray-500">종목 데이터를 불러오는 중...</p>
          </div>
        </div>
      </main>
    );
  }
  
  if (error) {
    return (
      <main className="min-h-screen bg-[#F9FAFB]">
        <header className="bg-white border-b border-gray-200 sticky top-0 z-10">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
            <h1 className="text-xl font-bold text-gray-900">전종목 리스트</h1>
            <p className="text-sm text-gray-500 mt-1">국내上市 전체 종목</p>
          </div>
        </header>
        <div className="flex items-center justify-center h-[calc(100vh-80px)]">
          <EmptyState
            variant="error"
            title="데이터 로드 실패"
            description={error}
          />
        </div>
      </main>
    );
  }
  
  return (
    <main className="min-h-screen bg-[#F9FAFB]">
      <Header />
      
      {/* Page Title */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <h1 className="text-xl font-bold text-gray-900">전종목 리스트</h1>
          <p className="text-sm text-gray-500 mt-1">국내上市 전체 종목</p>
        </div>
      </div>
      
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {/* Filters */}
        <div className="bg-white rounded-xl border border-gray-200 p-4 mb-4">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-sm font-semibold text-gray-900">필터</h2>
            <div className="flex items-center gap-2">
              {hasActiveFilters && (
                <button
                  onClick={clearFilters}
                  className="flex items-center gap-1 text-sm text-[#0045F6] hover:text-[#0037B6] transition-colors"
                >
                  <X className="w-4 h-4" />
                  필터 초기화
                </button>
              )}
              <button
                onClick={() => setShowAdvancedFilters(!showAdvancedFilters)}
                className="flex items-center gap-1 text-sm text-gray-600 hover:text-gray-900 transition-colors"
              >
                {showAdvancedFilters ? '간단히' : '상세필터'}
                {showAdvancedFilters ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
              </button>
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* PER Range Filter */}
            <div className="flex items-center gap-2">
              <span className="text-sm text-gray-600 whitespace-nowrap">PER:</span>
              <div className="flex items-center gap-1">
                <input
                  type="number"
                  placeholder="최소"
                  value={filters.perMin}
                  onChange={(e) => handleFilterChange('perMin', e.target.value)}
                  className="w-20 px-2 py-1.5 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#0045F6]/20 focus:border-[#0045F6]"
                />
                <span className="text-gray-400">~</span>
                <input
                  type="number"
                  placeholder="최대"
                  value={filters.perMax}
                  onChange={(e) => handleFilterChange('perMax', e.target.value)}
                  className="w-20 px-2 py-1.5 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#0045F6]/20 focus:border-[#0045F6]"
                />
                <span className="text-sm text-gray-500">배</span>
              </div>
            </div>
            
            {/* Market Cap Filter */}
            <div className="flex items-center gap-2">
              <span className="text-sm text-gray-600 whitespace-nowrap">시가총액:</span>
              <div className="flex items-center gap-1">
                <input
                  type="number"
                  placeholder="최소"
                  value={filters.marketCapMin}
                  onChange={(e) => handleFilterChange('marketCapMin', e.target.value)}
                  className="w-28 px-2 py-1.5 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#0045F6]/20 focus:border-[#0045F6]"
                />
                <span className="text-sm text-gray-500">조 이상</span>
              </div>
            </div>
            
            {/* Results count */}
            <div className="flex items-center justify-end text-sm text-gray-500">
              <span className="font-medium text-gray-900">{filteredAndSortedStocks.length}</span>
              <span>개 종목</span>
            </div>
          </div>
          
          {/* Advanced Filters */}
          {showAdvancedFilters && (
            <div className="mt-4 pt-4 border-t border-gray-200 grid grid-cols-1 md:grid-cols-3 gap-4">
              {/* PBR Range Filter */}
              <div className="flex items-center gap-2">
                <span className="text-sm text-gray-600 whitespace-nowrap">PBR:</span>
                <div className="flex items-center gap-1">
                  <input
                    type="number"
                    placeholder="최소"
                    value={filters.pbrMin}
                    onChange={(e) => handleFilterChange('pbrMin', e.target.value)}
                    className="w-20 px-2 py-1.5 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#0045F6]/20 focus:border-[#0045F6]"
                  />
                  <span className="text-gray-400">~</span>
                  <input
                    type="number"
                    placeholder="최대"
                    value={filters.pbrMax}
                    onChange={(e) => handleFilterChange('pbrMax', e.target.value)}
                    className="w-20 px-2 py-1.5 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#0045F6]/20 focus:border-[#0045F6]"
                  />
                  <span className="text-sm text-gray-500">배</span>
                </div>
              </div>
              
              {/* ROE Filter */}
              <div className="flex items-center gap-2">
                <span className="text-sm text-gray-600 whitespace-nowrap">
                  ROE:
                  <Tooltip text="자본이익률 - 높을수록 수익성良好" />
                </span>
                <div className="flex items-center gap-1">
                  <input
                    type="number"
                    placeholder="최소"
                    value={filters.roeMin}
                    onChange={(e) => handleFilterChange('roeMin', e.target.value)}
                    className="w-20 px-2 py-1.5 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#0045F6]/20 focus:border-[#0045F6]"
                  />
                  <span className="text-sm text-gray-500">% 이상</span>
                </div>
              </div>
              
              {/* Debt Ratio Filter */}
              <div className="flex items-center gap-2">
                <span className="text-sm text-gray-600 whitespace-nowrap">
                  부채비율:
                  <Tooltip text="부채/자본 - 낮을수록 안전" />
                </span>
                <div className="flex items-center gap-1">
                  <input
                    type="number"
                    placeholder="최대"
                    value={filters.debtRatioMax}
                    onChange={(e) => handleFilterChange('debtRatioMax', e.target.value)}
                    className="w-20 px-2 py-1.5 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#0045F6]/20 focus:border-[#0045F6]"
                  />
                  <span className="text-sm text-gray-500">% 이하</span>
                </div>
              </div>
              
              {/* Forward P/E Filter */}
              <div className="flex items-center gap-2">
                <span className="text-sm text-gray-600 whitespace-nowrap">
                  Forward P/E:
                  <Tooltip text="예상 PER - 낮을수록 저평가 가능" />
                </span>
                <div className="flex items-center gap-1">
                  <input
                    type="number"
                    placeholder="최대"
                    value={filters.forwardPeMax}
                    onChange={(e) => handleFilterChange('forwardPeMax', e.target.value)}
                    className="w-20 px-2 py-1.5 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#0045F6]/20 focus:border-[#0045F6]"
                  />
                  <span className="text-sm text-gray-500">배 이하</span>
                </div>
              </div>
              
              {/* RSI Filter */}
              <div className="flex items-center gap-2">
                <span className="text-sm text-gray-600 whitespace-nowrap">
                  RSI:
                  <Tooltip text="과매수(>70)/과매도(<30) 구간" />
                </span>
                <select
                  value={filters.rsiRange}
                  onChange={(e) => handleFilterChange('rsiRange', e.target.value)}
                  className="px-2 py-1.5 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#0045F6]/20 focus:border-[#0045F6]"
                >
                  <option value="all">전체</option>
                  <option value="oversold">과매도 (30↓)</option>
                  <option value="neutral">중립 (30~70)</option>
                  <option value="overbought">과매수 (70↑)</option>
                </select>
              </div>
              
              {/* Volume Spike Filter */}
              <div className="flex items-center gap-2">
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={filters.volumeSpike}
                    onChange={(e) => handleFilterChange('volumeSpike', e.target.checked)}
                    className="w-4 h-4 text-[#0045F6] border-gray-300 rounded focus:ring-[#0045F6]/20"
                  />
                  <span className="text-sm text-gray-600">
                    거래량 급등
                    <Tooltip text="전일 대비 2배 이상 거래량 증가" />
                  </span>
                </label>
              </div>
            </div>
          )}
        </div>
        
        {/* Sort Options */}
        <div className="flex items-center gap-2 mb-4 overflow-x-auto pb-2">
          {sortOptions.map((option) => (
            <button
              key={option.field}
              onClick={() => handleSort(option.field as SortField)}
              className={cn(
                "flex items-center gap-1 px-3 py-1.5 text-sm rounded-lg whitespace-nowrap transition-colors",
                sortField === option.field
                  ? "bg-[#0045F6] text-white"
                  : "bg-white text-gray-600 hover:bg-gray-100 border border-gray-200"
              )}
            >
              {option.label}
              {sortField === option.field && (
                sortDirection === 'asc' 
                  ? <ArrowUp className="w-3 h-3" />
                  : <ArrowDown className="w-3 h-3" />
              )}
            </button>
          ))}
        </div>
        
        {/* Stock Table */}
        <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="bg-gray-50 border-b border-gray-200">
                  <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">
                    종목
                  </th>
                  <th 
                    className="text-right px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100 transition-colors"
                    onClick={() => handleSort('market_cap')}
                  >
                    <div className="flex items-center justify-end gap-1">
                      시가총액
                      <SortIcon field="market_cap" />
                    </div>
                  </th>
                  <th className="text-right px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">
                    현재가
                  </th>
                  <th 
                    className="text-right px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100 transition-colors"
                    onClick={() => handleSort('change_rate')}
                  >
                    <div className="flex items-center justify-end gap-1">
                      등락률
                      <SortIcon field="change_rate" />
                    </div>
                  </th>
                  <th 
                    className="text-right px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100 transition-colors"
                    onClick={() => handleSort('per')}
                  >
                    <div className="flex items-center justify-end gap-1">
                      PER
                      <SortIcon field="per" />
                    </div>
                  </th>
                  <th 
                    className="text-right px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100 transition-colors"
                    onClick={() => handleSort('pbr')}
                  >
                    <div className="flex items-center justify-end gap-1">
                      PBR
                      <SortIcon field="pbr" />
                    </div>
                  </th>
                  {/* New columns */}
                  <th 
                    className="text-right px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100 transition-colors"
                    onClick={() => handleSort('roe')}
                  >
                    <div className="flex items-center justify-end gap-1">
                      ROE
                      <SortIcon field="roe" />
                    </div>
                  </th>
                  <th 
                    className="text-right px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100 transition-colors"
                    onClick={() => handleSort('debt_ratio')}
                  >
                    <div className="flex items-center justify-end gap-1">
                      부채비율
                      <SortIcon field="debt_ratio" />
                    </div>
                  </th>
                  <th 
                    className="text-right px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100 transition-colors"
                    onClick={() => handleSort('forward_pe')}
                  >
                    <div className="flex items-center justify-end gap-1">
                      Forward P/E
                      <SortIcon field="forward_pe" />
                    </div>
                  </th>
                  <th className="text-center px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">
                    기술적신호
                  </th>
                  {showAdvancedFilters && (
                    <th 
                      className="text-right px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100 transition-colors"
                      onClick={() => handleSort('recommendation_score')}
                    >
                      <div className="flex items-center justify-end gap-1">
                        추천점수
                        <SortIcon field="recommendation_score" />
                      </div>
                    </th>
                  )}
                </tr>
              </thead>
              <tbody>
                {paginatedStocks.map((stock) => {
                  const isPositive = stock.change_rate >= 0;
                  const signal = getTechnicalSignal(stock);
                  
                  // ROE color coding
                  const roeClass = cn(
                    "text-right px-4 py-3 text-sm",
                    stock.roe !== undefined && stock.roe >= 15 && "text-green-600 font-medium",
                    stock.roe !== undefined && stock.roe < 5 && stock.roe >= 0 && "text-red-600",
                    stock.roe !== undefined && stock.roe >= 5 && stock.roe < 15 && "text-yellow-600",
                  );
                  
                  // Debt ratio color coding
                  const debtRatioClass = cn(
                    "text-right px-4 py-3 text-sm",
                    stock.debt_ratio !== undefined && stock.debt_ratio < 100 && "text-green-600 font-medium",
                    stock.debt_ratio !== undefined && stock.debt_ratio >= 200 && "text-red-600",
                    stock.debt_ratio !== undefined && stock.debt_ratio >= 100 && stock.debt_ratio < 200 && "text-yellow-600",
                  );
                  
                  return (
                    <tr 
                      key={stock.ticker} 
                      className="border-b border-gray-100 hover:bg-[#F4F6FC] transition-colors cursor-pointer"
                    >
                      <td className="px-4 py-3">
                        <div className="flex flex-col">
                          <span className="font-semibold text-gray-900">{stock.ticker}</span>
                          <span className="text-sm text-gray-500 truncate max-w-[150px]">{stock.name}</span>
                        </div>
                      </td>
                      <td className="text-right px-4 py-3 text-sm text-gray-900 font-medium">
                        {formatMarketCap(stock.market_cap)}
                      </td>
                      <td className="text-right px-4 py-3 text-sm font-semibold text-gray-900">
                        {formatPrice(stock.current_price)}
                      </td>
                      <td className="text-right px-4 py-3">
                        <div 
                          className={cn(
                            "inline-flex items-center px-2 py-0.5 rounded text-sm font-medium",
                            isPositive 
                              ? "bg-[#E5493A]/10 text-[#E5493A]" 
                              : "bg-[#2972FF]/10 text-[#2972FF]"
                          )}
                        >
                          <span className="mr-1">
                            {isPositive ? '▲' : '▼'}
                          </span>
                          {Math.abs(stock.change_rate).toFixed(2)}%
                        </div>
                      </td>
                      <td className="text-right px-4 py-3 text-sm text-gray-900">
                        {formatRatio(stock.per)}배
                      </td>
                      <td className="text-right px-4 py-3 text-sm text-gray-900">
                        {formatRatio(stock.pbr)}배
                      </td>
                      {/* New columns */}
                      <td className={roeClass}>
                        {formatPercent(stock.roe)}
                      </td>
                      <td className={debtRatioClass}>
                        {formatPercent(stock.debt_ratio)}
                      </td>
                      <td className="text-right px-4 py-3 text-sm text-gray-900">
                        {formatRatio(stock.forward_pe)}배
                      </td>
                      <td className="text-center px-4 py-3">
                        <TechnicalBadge signal={signal} />
                      </td>
                      {showAdvancedFilters && (
                        <td className="text-right px-4 py-3 text-sm font-medium text-[#0045F6]">
                          {stock.recommendation_score !== undefined 
                            ? stock.recommendation_score.toFixed(0)
                            : '-'
                          }
                        </td>
                      )}
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
          
          {/* Empty state */}
          {paginatedStocks.length === 0 && (
            <EmptyState
              variant="filter"
              title="조건에 맞는 종목이 없습니다"
              description="필터 조건을 확인해주세요"
              actionLabel={hasActiveFilters ? "필터 초기화" : undefined}
              onAction={hasActiveFilters ? clearFilters : undefined}
            />
          )}
          
          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex items-center justify-between px-4 py-3 border-t border-gray-200 bg-gray-50">
              <div className="text-sm text-gray-500">
                <span className="font-medium text-gray-900">{(currentPage - 1) * ITEMS_PER_PAGE + 1}</span>
                {' - '}
                <span className="font-medium text-gray-900">{Math.min(currentPage * ITEMS_PER_PAGE, filteredAndSortedStocks.length)}</span>
                {' / '}
                <span>{filteredAndSortedStocks.length}</span>
              </div>
              
              <div className="flex items-center gap-1">
                <button
                  onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                  disabled={currentPage === 1}
                  className="p-2 rounded-lg border border-gray-200 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  <ChevronLeft className="w-4 h-4 text-gray-600" />
                </button>
                
                {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                  let pageNum: number;
                  if (totalPages <= 5) {
                    pageNum = i + 1;
                  } else if (currentPage <= 3) {
                    pageNum = i + 1;
                  } else if (currentPage >= totalPages - 2) {
                    pageNum = totalPages - 4 + i;
                  } else {
                    pageNum = currentPage - 2 + i;
                  }
                  
                  return (
                    <button
                      key={pageNum}
                      onClick={() => setCurrentPage(pageNum)}
                      className={cn(
                        "min-w-[36px] h-9 px-3 rounded-lg text-sm font-medium transition-colors",
                        currentPage === pageNum
                          ? "bg-[#0045F6] text-white"
                          : "text-gray-600 hover:bg-gray-100"
                      )}
                    >
                      {pageNum}
                    </button>
                  );
                })}
                
                <button
                  onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                  disabled={currentPage === totalPages}
                  className="p-2 rounded-lg border border-gray-200 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  <ChevronRight className="w-4 h-4 text-gray-600" />
                </button>
              </div>
            </div>
          )}
        </div>
        
        {/* Disclaimer */}
        <footer className="mt-6 p-4 bg-gray-50 rounded-xl border border-gray-200">
          <p className="text-xs text-gray-500 text-center">
            ⚠️ 본 서비스에서 제공하는 정보는 참고용으로서 투자 권유가 아닙니다. 투자 결정 전 반드시 본인의 투자 목표와 위험 감수를 확인하시기 바랍니다.
          </p>
        </footer>
      </div>
    </main>
  );
}
