'use client';

import { useState, useEffect, useRef } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { ArrowLeft, TrendingUp, TrendingDown, Building2, DollarSign, BarChart3, Activity } from 'lucide-react';
import { createChart, ColorType, IChartApi, ISeriesApi, CandlestickSeries, LineSeries, HistogramSeries } from 'lightweight-charts';
import type { StockDetail } from '@/types';
import EmptyState from '@/components/EmptyState';

/** Format price in KRW */
function formatPrice(price: number): string {
  return new Intl.NumberFormat('ko-KR', {
    style: 'currency',
    currency: 'KRW',
    maximumFractionDigits: 0,
  }).format(price);
}

/** Format ratio with 2 decimal places */
function formatRatio(value: number | undefined): string {
  if (value === undefined || value === null) return '-';
  return value.toFixed(2);
}

/** Format market cap */
function formatMarketCap(value: number | undefined): string {
  if (value === undefined || value === null) return '-';
  if (value >= 1_000_000_000_000) {
    return `${(value / 1_000_000_000_000).toFixed(2)}조원`;
  }
  return `${(value / 1_000_000_000).toFixed(0)}억원`;
}

/** Chart data point with indicators */
interface ChartDataPoint {
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
  ma_5?: number;
  ma_20?: number;
  ma_60?: number;
  rsi?: number;
}

/** Fetch real chart data from API */
async function fetchChartData(ticker: string, period: string = '3m'): Promise<ChartDataPoint[]> {
  const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  const response = await fetch(`${baseUrl}/api/stocks/${ticker}/chart?period=${period}`, {
    cache: 'no-store',
  });
  
  if (!response.ok) {
    throw new Error(`Failed to fetch chart data: ${response.status}`);
  }
  
  const data = await response.json();
  return data.data || [];
}

/** Fetch technical indicators from API */
async function fetchTechnicalIndicators(ticker: string): Promise<{
  ma_5: number;
  ma_20: number;
  ma_60: number;
  ma_120: number;
  rsi_14: number;
  rsi_signal: string;
  trend: string;
  volume_spike: boolean;
} | null> {
  try {
    const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    const response = await fetch(`${baseUrl}/api/stocks/${ticker}/technical`, {
      cache: 'no-store',
    });
    
    if (!response.ok) {
      return null;
    }
    
    return await response.json();
  } catch {
    return null;
  }
}

export default function StockDetailPage() {
  const params = useParams();
  const router = useRouter();
  const ticker = params.ticker as string;
  
  const [stock, setStock] = useState<StockDetail | null>(null);
  const [technicalData, setTechnicalData] = useState<any>(null);
  const [chartData, setChartData] = useState<ChartDataPoint[]>([]);
  const [chartLoading, setChartLoading] = useState(true);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const rsiContainerRef = useRef<HTMLDivElement>(null);
  const volumeContainerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const rsiChartRef = useRef<IChartApi | null>(null);
  const volumeChartRef = useRef<IChartApi | null>(null);
  const candlestickSeriesRef = useRef<ISeriesApi<'Candlestick'> | null>(null);
  const ma5SeriesRef = useRef<ISeriesApi<'Line'> | null>(null);
  const ma20SeriesRef = useRef<ISeriesApi<'Line'> | null>(null);
  const ma60SeriesRef = useRef<ISeriesApi<'Line'> | null>(null);
  const rsiSeriesRef = useRef<ISeriesApi<'Line'> | null>(null);
  const volumeSeriesRef = useRef<ISeriesApi<'Histogram'> | null>(null);

  // Fetch stock data
  useEffect(() => {
    async function fetchStock() {
      try {
        setLoading(true);
        setError(null);
        
        const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
        const response = await fetch(`${baseUrl}/api/stocks/${ticker}`, {
          cache: 'no-store',
        });
        
        if (response.status === 404) {
          setError(`종목 '${ticker}'를 찾을 수 없습니다`);
          return;
        }
        
        if (!response.ok) {
          throw new Error(`Failed to fetch stock: ${response.status}`);
        }
        
        const data = await response.json();
        setStock(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error');
      } finally {
        setLoading(false);
      }
    }
    
    if (ticker) {
      fetchStock();
    }
  }, [ticker]);

  // Fetch chart data and technical indicators
  useEffect(() => {
    async function fetchChartAndIndicators() {
      if (!ticker) return;
      
      try {
        setChartLoading(true);
        
        // Fetch both in parallel
        const [chartDataResult, technicalResult] = await Promise.all([
          fetchChartData(ticker, '3m'),
          fetchTechnicalIndicators(ticker),
        ]);
        
        setChartData(chartDataResult);
        setTechnicalData(technicalResult);
      } catch (err) {
        console.error('Error fetching chart data:', err);
      } finally {
        setChartLoading(false);
      }
    }
    
    fetchChartAndIndicators();
  }, [ticker]);

  // Initialize main price chart with MA overlays
  useEffect(() => {
    if (!chartContainerRef.current || chartData.length === 0 || chartRef.current) return;

    // Main price chart
    const chart = createChart(chartContainerRef.current, {
      layout: {
        background: { type: ColorType.Solid, color: '#ffffff' },
        textColor: '#333',
      },
      grid: {
        vertLines: { color: '#f0f0f0' },
        horzLines: { color: '#f0f0f0' },
      },
      crosshair: {
        mode: 1,
      },
      rightPriceScale: {
        borderColor: '#e0e0e0',
      },
      timeScale: {
        borderColor: '#e0e0e0',
        timeVisible: false,
      },
      width: chartContainerRef.current.clientWidth,
      height: 350,
    });

    // Candlestick series
    const candlestickSeries = chart.addSeries(CandlestickSeries, {
      upColor: '#E5493A',
      downColor: '#2972FF',
      borderUpColor: '#E5493A',
      borderDownColor: '#2972FF',
      wickUpColor: '#E5493A',
      wickDownColor: '#2972FF',
    });

    // MA line series
    const ma5Series = chart.addSeries(LineSeries, {
      color: '#FF6B6B',
      lineWidth: 1,
      title: 'MA5',
    });
    
    const ma20Series = chart.addSeries(LineSeries, {
      color: '#4ECDC4',
      lineWidth: 1,
      title: 'MA20',
    });
    
    const ma60Series = chart.addSeries(LineSeries, {
      color: '#45B7D1',
      lineWidth: 2,
      title: 'MA60',
    });

    // Set candlestick data
    const candleData = chartData.map(d => ({
      time: d.date as any,
      open: d.open,
      high: d.high,
      low: d.low,
      close: d.close,
    }));
    candlestickSeries.setData(candleData);

    // Set MA data (filter out undefined values)
    const ma5Data = chartData
      .filter(d => d.ma_5 !== undefined && d.ma_5 !== null)
      .map(d => ({ time: d.date as any, value: d.ma_5! }));
    ma5Series.setData(ma5Data);

    const ma20Data = chartData
      .filter(d => d.ma_20 !== undefined && d.ma_20 !== null)
      .map(d => ({ time: d.date as any, value: d.ma_20! }));
    ma20Series.setData(ma20Data);

    const ma60Data = chartData
      .filter(d => d.ma_60 !== undefined && d.ma_60 !== null)
      .map(d => ({ time: d.date as any, value: d.ma_60! }));
    ma60Series.setData(ma60Data);

    chart.timeScale().fitContent();

    chartRef.current = chart;
    candlestickSeriesRef.current = candlestickSeries;
    ma5SeriesRef.current = ma5Series;
    ma20SeriesRef.current = ma20Series;
    ma60SeriesRef.current = ma60Series;

    // Handle resize
    const handleResize = () => {
      if (chartContainerRef.current && chartRef.current) {
        chartRef.current.applyOptions({
          width: chartContainerRef.current.clientWidth,
        });
      }
    };

    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      if (chartRef.current) {
        chartRef.current.remove();
        chartRef.current = null;
      }
    };
  }, [chartData]);

  // Initialize Volume chart
  useEffect(() => {
    if (!volumeContainerRef.current || chartData.length === 0 || volumeChartRef.current) return;

    const volumeChart = createChart(volumeContainerRef.current, {
      layout: {
        background: { type: ColorType.Solid, color: '#ffffff' },
        textColor: '#333',
      },
      grid: {
        vertLines: { color: '#f0f0f0' },
        horzLines: { color: '#f0f0f0' },
      },
      rightPriceScale: {
        borderColor: '#e0e0e0',
      },
      timeScale: {
        borderColor: '#e0e0e0',
        timeVisible: false,
        visible: false, // Hide time scale on volume chart
      },
      width: volumeContainerRef.current.clientWidth,
      height: 80,
    });

    const volumeSeries = volumeChart.addSeries(HistogramSeries, {
      color: '#26a69a',
      priceFormat: {
        type: 'volume',
      },
    });

    const volumeData = chartData.map(d => ({
      time: d.date as any,
      value: d.volume,
      color: d.close >= d.open ? '#E5493A' : '#2972FF',
    }));

    volumeSeries.setData(volumeData);
    volumeChart.timeScale().fitContent();

    volumeChartRef.current = volumeChart;
    volumeSeriesRef.current = volumeSeries;

    // Sync time scales
    const mainChart = chartRef.current;
    if (mainChart) {
      volumeChart.timeScale().subscribeVisibleTimeRangeChange((timeRange) => {
        if (timeRange) {
          mainChart.timeScale().setVisibleRange(timeRange);
        }
      });
    }

    const handleResize = () => {
      if (volumeContainerRef.current && volumeChartRef.current) {
        volumeChartRef.current.applyOptions({
          width: volumeContainerRef.current.clientWidth,
        });
      }
    };

    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      if (volumeChartRef.current) {
        volumeChartRef.current.remove();
        volumeChartRef.current = null;
      }
    };
  }, [chartData]);

  // Initialize RSI chart
  useEffect(() => {
    if (!rsiContainerRef.current || chartData.length === 0 || !chartData.some(d => d.rsi !== undefined) || rsiChartRef.current) return;

    const rsiChart = createChart(rsiContainerRef.current, {
      layout: {
        background: { type: ColorType.Solid, color: '#ffffff' },
        textColor: '#333',
      },
      grid: {
        vertLines: { color: '#f0f0f0' },
        horzLines: { color: '#f0f0f0' },
      },
      rightPriceScale: {
        borderColor: '#e0e0e0',
      },
      timeScale: {
        borderColor: '#e0e0e0',
        timeVisible: false,
        visible: false, // Hide time scale on RSI chart
      },
      width: rsiContainerRef.current.clientWidth,
      height: 100,
    });

    const rsiSeries = rsiChart.addSeries(LineSeries, {
      color: '#8B5CF6',
      lineWidth: 2,
    });

    // Add overbought/oversold lines
    const overboughtLine = rsiChart.addSeries(LineSeries, {
      color: '#E5493A',
      lineWidth: 1,
      lineStyle: 2, // Dashed
      lastValueVisible: false,
      title: 'Overbought (70)',
    });

    const oversoldLine = rsiChart.addSeries(LineSeries, {
      color: '#2972FF',
      lineWidth: 1,
      lineStyle: 2, // Dashed
      lastValueVisible: false,
      title: 'Oversold (30)',
    });

    const rsiData = chartData
      .filter(d => d.rsi !== undefined && d.rsi !== null)
      .map(d => ({ time: d.date as any, value: d.rsi! }));
    rsiSeries.setData(rsiData);

    // Set horizontal reference lines
    if (rsiData.length > 0) {
      const firstTime = rsiData[0].time;
      const lastTime = rsiData[rsiData.length - 1].time;
      overboughtLine.setData([
        { time: firstTime, value: 70 },
        { time: lastTime, value: 70 },
      ]);
      oversoldLine.setData([
        { time: firstTime, value: 30 },
        { time: lastTime, value: 30 },
      ]);
    }

    rsiChart.timeScale().fitContent();

    rsiChartRef.current = rsiChart;
    rsiSeriesRef.current = rsiSeries;

    // Sync time scales
    const mainChartForRsi = chartRef.current;
    if (mainChartForRsi) {
      rsiChart.timeScale().subscribeVisibleTimeRangeChange((timeRange) => {
        if (timeRange) {
          mainChartForRsi.timeScale().setVisibleRange(timeRange);
        }
      });
    }

    const handleResize = () => {
      if (rsiContainerRef.current && rsiChartRef.current) {
        rsiChartRef.current.applyOptions({
          width: rsiContainerRef.current.clientWidth,
        });
      }
    };

    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      if (rsiChartRef.current) {
        rsiChartRef.current.remove();
        rsiChartRef.current = null;
      }
    };
  }, [chartData]);

  // Loading state
  if (loading) {
    return (
      <main className="min-h-screen bg-[#F9FAFB]">
        <header className="bg-white border-b border-gray-200 sticky top-0 z-10">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
            <button
              onClick={() => router.push('/stocks')}
              className="flex items-center gap-2 text-gray-600 hover:text-gray-900 transition-colors"
            >
              <ArrowLeft className="w-5 h-5" />
              <span className="text-sm font-medium">목록으로</span>
            </button>
          </div>
        </header>
        <div className="flex items-center justify-center h-[calc(100vh-80px)]">
          <div className="flex flex-col items-center gap-3">
            <div className="w-8 h-8 border-4 border-[#0045F6] border-t-transparent rounded-full animate-spin" />
            <p className="text-gray-500">종목 정보를 불러오는 중...</p>
          </div>
        </div>
      </main>
    );
  }

  // Error state
  if (error || !stock) {
    return (
      <main className="min-h-screen bg-[#F9FAFB]">
        <header className="bg-white border-b border-gray-200 sticky top-0 z-10">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
            <button
              onClick={() => router.push('/stocks')}
              className="flex items-center gap-2 text-gray-600 hover:text-gray-900 transition-colors"
            >
              <ArrowLeft className="w-5 h-5" />
              <span className="text-sm font-medium">목록으로</span>
            </button>
          </div>
        </header>
        <div className="flex items-center justify-center h-[calc(100vh-80px)]">
          <EmptyState
            variant="error"
            title={error || '종목을 찾을 수 없습니다'}
            description="올바른 종목 코드인지 확인해주세요"
            actionLabel="전종목 리스트로 이동"
            onAction={() => router.push('/stocks')}
          />
        </div>
      </main>
    );
  }

  const isPositive = stock.change_rate >= 0;
  const changeColor = isPositive ? 'text-[#E5493A]' : 'text-[#2972FF]';
  const changeBgColor = isPositive ? 'bg-[#E5493A]/10' : 'bg-[#2972FF]/10';

  // Get trend display
  const getTrendDisplay = (trend: string) => {
    switch (trend) {
      case 'strong_uptrend':
        return { text: '강한 상승세', color: 'text-green-600', bg: 'bg-green-100' };
      case 'uptrend':
        return { text: '상승세', color: 'text-green-600', bg: 'bg-green-50' };
      case 'strong_downtrend':
        return { text: '강한 하락세', color: 'text-red-600', bg: 'bg-red-100' };
      case 'downtrend':
        return { text: '하락세', color: 'text-red-600', bg: 'bg-red-50' };
      default:
        return { text: '횡보', color: 'text-gray-600', bg: 'bg-gray-100' };
    }
  };

  const trendDisplay = technicalData ? getTrendDisplay(technicalData.trend) : null;
  const rsiDisplay = technicalData ? {
    value: technicalData.rsi_14,
    signal: technicalData.rsi_signal,
    color: technicalData.rsi_signal === 'overbought' ? 'text-red-600' : 
           technicalData.rsi_signal === 'oversold' ? 'text-blue-600' : 'text-gray-600',
  } : null;

  return (
    <main className="min-h-screen bg-[#F9FAFB]">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <button
            onClick={() => router.push('/stocks')}
            className="flex items-center gap-2 text-gray-600 hover:text-gray-900 transition-colors"
          >
            <ArrowLeft className="w-5 h-5" />
            <span className="text-sm font-medium">목록으로</span>
          </button>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {/* Stock Header Card */}
        <div className="bg-white rounded-xl border border-gray-200 p-6 mb-6">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            <div className="flex items-center gap-4">
              <div className="w-16 h-16 bg-[#0045F6]/10 rounded-xl flex items-center justify-center">
                <Building2 className="w-8 h-8 text-[#0045F6]" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">{stock.name}</h1>
                <p className="text-lg text-gray-500">{stock.ticker}</p>
              </div>
            </div>
            
            <div className="text-left md:text-right">
              <p className="text-3xl font-bold text-gray-900">{formatPrice(stock.current_price)}</p>
              <div className={`inline-flex items-center gap-1 px-3 py-1 rounded-lg ${changeBgColor} ${changeColor} mt-2`}>
                {isPositive ? (
                  <TrendingUp className="w-4 h-4" />
                ) : (
                  <TrendingDown className="w-4 h-4" />
                )}
                <span className="font-semibold">
                  {isPositive ? '+' : ''}{stock.change_rate.toFixed(2)}%
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Technical Indicators Row */}
        {technicalData && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            {/* Trend */}
            <div className="bg-white rounded-xl border border-gray-200 p-4">
              <div className="flex items-center gap-2 text-gray-500 mb-2">
                <TrendingUp className="w-4 h-4" />
                <span className="text-sm">추세</span>
              </div>
              <p className={`text-lg font-bold ${trendDisplay?.color}`}>
                {trendDisplay?.text}
              </p>
            </div>

            {/* RSI */}
            <div className="bg-white rounded-xl border border-gray-200 p-4">
              <div className="flex items-center gap-2 text-gray-500 mb-2">
                <Activity className="w-4 h-4" />
                <span className="text-sm">RSI (14)</span>
              </div>
              <p className={`text-lg font-bold ${rsiDisplay?.color}`}>
                {rsiDisplay?.value ? rsiDisplay.value.toFixed(2) : '-'}
                <span className="text-sm font-normal text-gray-500 ml-1">
                  ({rsiDisplay?.signal === 'overbought' ? '과매수' : 
                    rsiDisplay?.signal === 'oversold' ? '과매도' : '중립'})
                </span>
              </p>
            </div>

            {/* MA Status */}
            <div className="bg-white rounded-xl border border-gray-200 p-4">
              <div className="flex items-center gap-2 text-gray-500 mb-2">
                <BarChart3 className="w-4 h-4" />
                <span className="text-sm">이평선</span>
              </div>
              <p className="text-lg font-bold text-gray-900">
                {technicalData.close > technicalData.ma_20 ? '상회' : '하회'}
                <span className="text-sm font-normal text-gray-500 ml-1">(MA20)</span>
              </p>
            </div>

            {/* Volume Spike */}
            <div className="bg-white rounded-xl border border-gray-200 p-4">
              <div className="flex items-center gap-2 text-gray-500 mb-2">
                <BarChart3 className="w-4 h-4" />
                <span className="text-sm">거래량</span>
              </div>
              <p className={`text-lg font-bold ${technicalData.volume_spike ? 'text-purple-600' : 'text-gray-900'}`}>
                {technicalData.volume_spike ? '급증' : '보통'}
              </p>
            </div>
          </div>
        )}

        {/* Metrics Grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          {/* PER */}
          <div className="bg-white rounded-xl border border-gray-200 p-4">
            <div className="flex items-center gap-2 text-gray-500 mb-2">
              <BarChart3 className="w-4 h-4" />
              <span className="text-sm">PER</span>
            </div>
            <p className="text-xl font-bold text-gray-900">
              {formatRatio(stock.per)}
              <span className="text-sm font-normal text-gray-500 ml-1">배</span>
            </p>
          </div>

          {/* PBR */}
          <div className="bg-white rounded-xl border border-gray-200 p-4">
            <div className="flex items-center gap-2 text-gray-500 mb-2">
              <BarChart3 className="w-4 h-4" />
              <span className="text-sm">PBR</span>
            </div>
            <p className="text-xl font-bold text-gray-900">
              {formatRatio(stock.pbr)}
              <span className="text-sm font-normal text-gray-500 ml-1">배</span>
            </p>
          </div>

          {/* Market Cap */}
          <div className="bg-white rounded-xl border border-gray-200 p-4">
            <div className="flex items-center gap-2 text-gray-500 mb-2">
              <DollarSign className="w-4 h-4" />
              <span className="text-sm">시가총액</span>
            </div>
            <p className="text-xl font-bold text-gray-900">
              {formatMarketCap(stock.market_cap)}
            </p>
          </div>

          {/* Forward P/E (calculated from EPS) */}
          <div className="bg-white rounded-xl border border-gray-200 p-4">
            <div className="flex items-center gap-2 text-gray-500 mb-2">
              <TrendingUp className="w-4 h-4" />
              <span className="text-sm">EPS</span>
            </div>
            <p className="text-xl font-bold text-gray-900">
              {formatRatio(stock.eps)}
              <span className="text-sm font-normal text-gray-500 ml-1">원</span>
            </p>
          </div>
        </div>

        {/* Additional Metrics Row */}
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-6">
          {/* BPS */}
          <div className="bg-white rounded-xl border border-gray-200 p-4">
            <p className="text-sm text-gray-500 mb-1">BPS (주당순자산)</p>
            <p className="text-lg font-semibold text-gray-900">
              {stock.bps ? formatPrice(stock.bps) : '-'}
            </p>
          </div>

          {/* Forward P/E Calculation */}
          <div className="bg-white rounded-xl border border-gray-200 p-4">
            <p className="text-sm text-gray-500 mb-1">Forward P/E</p>
            <p className="text-lg font-semibold text-gray-900">
              {stock.per && stock.per > 0 ? formatRatio(stock.per * 0.9) : '-'}
              <span className="text-sm font-normal text-gray-500 ml-1">배</span>
            </p>
          </div>

          {/* Price Change Amount */}
          <div className="bg-white rounded-xl border border-gray-200 p-4">
            <p className="text-sm text-gray-500 mb-1">전일대비</p>
            <p className={`text-lg font-semibold ${changeColor}`}>
              {isPositive ? '+' : ''}
              {formatPrice(stock.current_price * stock.change_rate / 100)}
            </p>
          </div>
        </div>

        {/* Chart Section */}
        <div className="bg-white rounded-xl border border-gray-200 p-6 mb-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900">주가 차트</h2>
            <div className="flex items-center gap-4 text-xs">
              <div className="flex items-center gap-1">
                <div className="w-3 h-0.5 bg-[#FF6B6B]" />
                <span className="text-gray-500">MA5</span>
              </div>
              <div className="flex items-center gap-1">
                <div className="w-3 h-0.5 bg-[#4ECDC4]" />
                <span className="text-gray-500">MA20</span>
              </div>
              <div className="flex items-center gap-1">
                <div className="w-3 h-0.5 bg-[#45B7D1]" />
                <span className="text-gray-500">MA60</span>
              </div>
            </div>
          </div>
          
          {chartLoading ? (
            <div className="flex items-center justify-center h-[350px]">
              <div className="flex flex-col items-center gap-3">
                <div className="w-8 h-8 border-4 border-[#0045F6] border-t-transparent rounded-full animate-spin" />
                <p className="text-gray-500">차트 데이터를 불러오는 중...</p>
              </div>
            </div>
          ) : chartData.length > 0 ? (
            <>
              {/* Main Price Chart */}
              <div ref={chartContainerRef} className="w-full" style={{ height: 350 }} />
              
              {/* Volume Chart */}
              <div ref={volumeContainerRef} className="w-full mt-1" style={{ height: 80 }} />
              
              {/* RSI Chart */}
              {chartData.some(d => d.rsi !== undefined) && (
                <div className="mt-4">
                  <h3 className="text-sm font-medium text-gray-700 mb-2">RSI (14)</h3>
                  <div ref={rsiContainerRef} className="w-full" style={{ height: 100 }} />
                </div>
              )}
            </>
          ) : (
            <div className="flex items-center justify-center h-[350px] text-gray-500">
              차트 데이터를 불러올 수 없습니다
            </div>
          )}
          
          <p className="text-xs text-gray-400 mt-2 text-center">
            * 과거 3개월간의 실제 거래 데이터 기준
          </p>
        </div>

        {/* Disclaimer */}
        <footer className="p-4 bg-gray-50 rounded-xl border border-gray-200">
          <p className="text-xs text-gray-500 text-center">
            ⚠️ 본 서비스에서 제공하는 정보는 참고용으로서 투자 권유가 아닙니다. 투자 결정 전 반드시 본인의 투자 목표와 위험 감수를 확인하시기 바랍니다.
          </p>
        </footer>
      </div>
    </main>
  );
}
