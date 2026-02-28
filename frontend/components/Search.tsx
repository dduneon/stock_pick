'use client';

import { useState, useEffect, useCallback, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { Search, X, TrendingUp, TrendingDown, Loader2 } from 'lucide-react';
import type { Stock } from '@/types';

interface SearchSuggestion {
  ticker: string;
  name: string;
  current_price: number;
  change_rate: number;
}

export default function SearchComponent() {
  const router = useRouter();
  const [query, setQuery] = useState('');
  const [suggestions, setSuggestions] = useState<SearchSuggestion[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [showDropdown, setShowDropdown] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const debounceTimerRef = useRef<NodeJS.Timeout | null>(null);

  // Close dropdown when clicking outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(event.target as Node) &&
        inputRef.current &&
        !inputRef.current.contains(event.target as Node)
      ) {
        setShowDropdown(false);
      }
    }

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Fetch suggestions with debounce
  const fetchSuggestions = useCallback(async (searchQuery: string) => {
    if (!searchQuery.trim()) {
      setSuggestions([]);
      setIsLoading(false);
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(
        `${baseUrl}/api/search?q=${encodeURIComponent(searchQuery)}`,
        { cache: 'no-store' }
      );

      if (!response.ok) {
        throw new Error('Failed to fetch suggestions');
      }

      const data: Stock[] = await response.json();
      // Limit to 6 suggestions for dropdown
      setSuggestions(data.slice(0, 6).map(stock => ({
        ticker: stock.ticker,
        name: stock.name,
        current_price: stock.current_price,
        change_rate: stock.change_rate,
      })));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch');
      setSuggestions([]);
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Handle input change with debounce
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setQuery(value);
    setShowDropdown(true);

    // Clear existing timer
    if (debounceTimerRef.current) {
      clearTimeout(debounceTimerRef.current);
    }

    // Set new timer (300ms debounce)
    debounceTimerRef.current = setTimeout(() => {
      fetchSuggestions(value);
    }, 300);
  };

  // Handle suggestion click
  const handleSuggestionClick = (ticker: string) => {
    setQuery('');
    setShowDropdown(false);
    setSuggestions([]);
    router.push(`/stocks/${ticker}`);
  };

  // Handle form submission
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      setShowDropdown(false);
      router.push(`/search?q=${encodeURIComponent(query.trim())}`);
    }
  };

  // Clear search
  const handleClear = () => {
    setQuery('');
    setSuggestions([]);
    setShowDropdown(false);
    inputRef.current?.focus();
  };

  // Format price
  const formatPrice = (price: number): string => {
    return new Intl.NumberFormat('ko-KR', {
      style: 'currency',
      currency: 'KRW',
      maximumFractionDigits: 0,
    }).format(price);
  };

  const hasResults = suggestions.length > 0;

  return (
    <div className="relative w-full max-w-md" ref={dropdownRef}>
      <form onSubmit={handleSubmit} className="relative">
        <div className="relative flex items-center">
          <Search className="absolute left-3 w-5 h-5 text-gray-400 pointer-events-none" />
          <input
            ref={inputRef}
            type="text"
            value={query}
            onChange={handleInputChange}
            onFocus={() => query.trim() && setShowDropdown(true)}
            placeholder="종목명 또는 티커 검색"
            className="w-full pl-10 pr-10 py-2.5 text-sm bg-gray-50 border border-gray-200 rounded-xl 
                       placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-[#0045F6]/20 
                       focus:border-[#0045F6] focus:bg-white transition-all duration-200"
            autoComplete="off"
          />
          {query && (
            <button
              type="button"
              onClick={handleClear}
              className="absolute right-3 p-1 rounded-full hover:bg-gray-200 transition-colors"
            >
              <X className="w-4 h-4 text-gray-400" />
            </button>
          )}
        </div>
      </form>

      {/* Autocomplete Dropdown */}
      {showDropdown && query.trim() && (
        <div className="absolute top-full left-0 right-0 mt-2 bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden z-50">
          {/* Loading State */}
          {isLoading && (
            <div className="flex items-center justify-center py-6">
              <Loader2 className="w-5 h-5 text-[#0045F6] animate-spin" />
              <span className="ml-2 text-sm text-gray-500">검색 중...</span>
            </div>
          )}

          {/* Error State */}
          {!isLoading && error && (
            <div className="py-6 text-center">
              <p className="text-sm text-gray-500">검색 중 오류가 발생했습니다</p>
            </div>
          )}

          {/* Empty State */}
          {!isLoading && !error && !hasResults && (
            <div className="py-6 text-center">
              <p className="text-sm text-gray-500">검색 결과가 없습니다</p>
              <p className="text-xs text-gray-400 mt-1">
                다른 검색어를 입력핫세요
              </p>
            </div>
          )}

          {/* Suggestions List */}
          {!isLoading && !error && hasResults && (
            <ul className="py-2">
              {suggestions.map((suggestion, index) => {
                const isPositive = suggestion.change_rate >= 0;
                return (
                  <li
                    key={suggestion.ticker}
                    onClick={() => handleSuggestionClick(suggestion.ticker)}
                    className="px-4 py-3 hover:bg-[#F4F6FC] cursor-pointer transition-colors
                               animate-in fade-in slide-in-from-top-1 duration-200"
                    style={{ animationDelay: `${index * 50}ms` }}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2">
                          <span className="font-semibold text-gray-900">
                            {suggestion.ticker}
                          </span>
                          <span className="text-sm text-gray-500 truncate">
                            {suggestion.name}
                          </span>
                        </div>
                      </div>
                      <div className="flex items-center gap-3 ml-4">
                        <span className="text-sm font-medium text-gray-900">
                          {formatPrice(suggestion.current_price)}
                        </span>
                        <div
                          className={`flex items-center gap-0.5 text-xs font-medium ${
                            isPositive
                              ? 'text-[#E5493A]'
                              : 'text-[#2972FF]'
                          }`}
                        >
                          {isPositive ? (
                            <TrendingUp className="w-3 h-3" />
                          ) : (
                            <TrendingDown className="w-3 h-3" />
                          )}
                          {Math.abs(suggestion.change_rate).toFixed(2)}%
                        </div>
                      </div>
                    </div>
                  </li>
                );
              })}
            </ul>
          )}

          {/* View All Results Link */}
          {!isLoading && !error && hasResults && (
            <div className="border-t border-gray-100">
              <button
                onClick={handleSubmit}
                className="w-full py-3 text-sm text-[#0045F6] font-medium hover:bg-[#F4F6FC] transition-colors"
              >
                전체 결과 보기
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
