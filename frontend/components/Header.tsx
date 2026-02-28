import Link from 'next/link';
import Search from './Search';

interface HeaderProps {
  title?: string;
  subtitle?: string;
  showSearch?: boolean;
}

export default function Header({ title, subtitle, showSearch = true }: HeaderProps) {
  return (
    <header className="bg-white border-b border-gray-200 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16 gap-4">
          {/* Logo/Title Section */}
          <div className="flex-shrink-0">
            <Link href="/" className="flex items-center gap-2">
              <div className="w-8 h-8 bg-[#0045F6] rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">S</span>
              </div>
              <span className="font-semibold text-gray-900 hidden sm:block">StockPick</span>
            </Link>
          </div>

          {/* Search Section */}
          {showSearch && (
            <div className="flex-1 max-w-md">
              <Search />
            </div>
          )}

          {/* Navigation */}
          <nav className="flex items-center gap-1 sm:gap-2">
            <Link
              href="/"
              className="px-3 py-2 text-sm font-medium text-gray-600 hover:text-gray-900 hover:bg-gray-50 rounded-lg transition-colors"
            >
              <span className="hidden sm:inline">추천</span>
              <span className="sm:hidden">추천</span>
            </Link>
            <Link
              href="/stocks"
              className="px-3 py-2 text-sm font-medium text-gray-600 hover:text-gray-900 hover:bg-gray-50 rounded-lg transition-colors"
            >
              <span className="hidden sm:inline">전종목</span>
              <span className="sm:hidden">종목</span>
            </Link>
          </nav>
        </div>
      </div>
    </header>
  );
}
