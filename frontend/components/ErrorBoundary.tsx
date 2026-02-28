'use client';

import { Component, ReactNode, ErrorInfo } from 'react';
import { AlertCircle, RefreshCw } from 'lucide-react';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
}

/**
 * Error Boundary component that catches JavaScript errors in child components
 * and displays a fallback UI instead of crashing the app.
 * 
 * Usage:
 * ```tsx
 * <ErrorBoundary>
 *   <YourComponent />
 * </ErrorBoundary>
 * ```
 */
export default class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
    };
  }

  static getDerivedStateFromError(error: Error): State {
    return {
      hasError: true,
      error,
      errorInfo: null,
    };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
    this.setState({
      error,
      errorInfo,
    });

    // Log error to console in development
    if (process.env.NODE_ENV === 'development') {
      console.error('ErrorBoundary caught an error:', error);
      console.error('Component stack:', errorInfo.componentStack);
    }
  }

  private handleReload = (): void => {
    if (typeof window !== 'undefined') {
      window.location.reload();
    }
  };

  private handleGoHome = (): void => {
    if (typeof window !== 'undefined') {
      window.location.href = '/';
    }
  };

  render(): ReactNode {
    if (this.state.hasError) {
      // Custom fallback UI
      if (this.props.fallback) {
        return this.props.fallback;
      }

      // Default fallback UI with Toss UI styling
      return (
        <div className="min-h-screen bg-[#F9FAFB] flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl border border-gray-200 p-8 max-w-md w-full text-center shadow-sm">
            {/* Error Icon */}
            <div className="w-16 h-16 bg-[#E5493A]/10 rounded-full flex items-center justify-center mx-auto mb-6">
              <AlertCircle className="w-8 h-8 text-[#E5493A]" />
            </div>

            {/* Error Title */}
            <h1 className="text-xl font-bold text-gray-900 mb-2">
              오류가 발생했습니다
            </h1>

            {/* Error Description */}
            <p className="text-sm text-gray-500 mb-2">
              페이지를 표시하는 중 문제가 발생했습니다.
            </p>
            <p className="text-xs text-gray-400 mb-6">
              잠시 후 다시 시도해주세요.
            </p>

            {/* Error Details (Development Only) */}
            {process.env.NODE_ENV === 'development' && this.state.error && (
              <div className="mb-6 text-left">
                <details className="bg-gray-50 rounded-lg p-4">
                  <summary className="text-sm font-medium text-gray-700 cursor-pointer">
                    오류 상세 정보
                  </summary>
                  <pre className="mt-2 text-xs text-red-600 overflow-auto max-h-32">
                    {this.state.error.message}
                    {this.state.errorInfo?.componentStack}
                  </pre>
                </details>
              </div>
            )}

            {/* Action Buttons */}
            <div className="flex flex-col sm:flex-row gap-3">
              <button
                onClick={this.handleReload}
                className="flex items-center justify-center gap-2 px-4 py-2.5 bg-[#0045F6] text-white rounded-xl font-medium hover:bg-[#0037B6] active:bg-[#002DA6] transition-colors"
              >
                <RefreshCw className="w-4 h-4" />
                새로고침
              </button>
              <button
                onClick={this.handleGoHome}
                className="px-4 py-2.5 text-gray-600 font-medium hover:text-gray-900 hover:bg-gray-50 rounded-xl transition-colors"
              >
                홈으로 이동
              </button>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
