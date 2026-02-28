import { ReactNode } from 'react';
import { Search, FileX, Filter, AlertCircle, LucideIcon } from 'lucide-react';

export type EmptyStateVariant = 'search' | 'filter' | 'error' | 'data';

interface EmptyStateProps {
  /** Main title for the empty state */
  title: string;
  /** Description text explaining the empty state */
  description?: string;
  /** Variant to determine icon and default styling */
  variant?: EmptyStateVariant;
  /** Custom icon component (overrides variant icon) */
  icon?: LucideIcon;
  /** Custom icon element (overrides icon prop) */
  customIcon?: ReactNode;
  /** Primary action button text */
  actionLabel?: string;
  /** Primary action button handler */
  onAction?: () => void;
  /** Secondary action button text */
  secondaryActionLabel?: string;
  /** Secondary action button handler */
  onSecondaryAction?: () => void;
  /** Additional CSS classes */
  className?: string;
  /** Whether to use compact padding */
  compact?: boolean;
}

/**
 * Reusable Empty State component for displaying when there's no data,
 * search results, or when an error occurs.
 * 
 * @example
 * ```tsx
 * // Search empty state
 * <EmptyState
 *   variant="search"
 *   title="검색 결과가 없습니다"
 *   description="다른 검색어를 입력핫세요"
 * />
 * 
 * // Filter empty state
 * <EmptyState
 *   variant="filter"
 *   title="조건에 맞는 종목이 없습니다"
 *   description="필터 조건을 확인해주세요"
 *   actionLabel="필터 초기화"
 *   onAction={clearFilters}
 * />
 * 
 * // Custom icon
 * <EmptyState
 *   title="데이터가 없습니다"
 *   icon={FileX}
 * />
 * ```
 */
export default function EmptyState({
  title,
  description,
  variant = 'data',
  icon,
  customIcon,
  actionLabel,
  onAction,
  secondaryActionLabel,
  onSecondaryAction,
  className = '',
  compact = false,
}: EmptyStateProps) {
  // Get icon based on variant
  const getVariantIcon = (): LucideIcon => {
    switch (variant) {
      case 'search':
        return Search;
      case 'filter':
        return Filter;
      case 'error':
        return AlertCircle;
      case 'data':
      default:
        return FileX;
    }
  };

  // Get icon color based on variant
  const getIconColors = (): { bg: string; icon: string } => {
    switch (variant) {
      case 'search':
        return { bg: 'bg-gray-100', icon: 'text-gray-400' };
      case 'filter':
        return { bg: 'bg-gray-100', icon: 'text-gray-400' };
      case 'error':
        return { bg: 'bg-[#E5493A]/10', icon: 'text-[#E5493A]' };
      case 'data':
      default:
        return { bg: 'bg-gray-100', icon: 'text-gray-400' };
    }
  };

  const IconComponent = icon || getVariantIcon();
  const { bg: bgColor, icon: iconColor } = getIconColors();

  return (
    <div
      className={`text-center ${compact ? 'py-8' : 'py-16'} ${className}`}
      role="status"
      aria-live="polite"
    >
      {/* Icon */}
      {customIcon || (
        <div
          className={`${compact ? 'w-12 h-12' : 'w-16 h-16'} ${bgColor} rounded-full flex items-center justify-center mx-auto mb-4`}
        >
          <IconComponent className={`${compact ? 'w-6 h-6' : 'w-8 h-8'} ${iconColor}`} />
        </div>
      )}

      {/* Title */}
      <h3 className={`font-medium text-gray-900 mb-2 ${compact ? 'text-base' : 'text-lg'}`}>
        {title}
      </h3>

      {/* Description */}
      {description && (
        <p className={`text-gray-500 ${compact ? 'text-sm' : 'text-base'} mb-4`}>
          {description}
        </p>
      )}

      {/* Actions */}
      {(actionLabel || secondaryActionLabel) && (
        <div className="flex flex-col sm:flex-row items-center justify-center gap-3 mt-4">
          {actionLabel && onAction && (
            <button
              onClick={onAction}
              className="px-4 py-2 bg-[#0045F6] text-white rounded-lg font-medium text-sm hover:bg-[#0037B6] active:bg-[#002DA6] transition-colors"
            >
              {actionLabel}
            </button>
          )}
          {secondaryActionLabel && onSecondaryAction && (
            <button
              onClick={onSecondaryAction}
              className="px-4 py-2 text-gray-600 font-medium text-sm hover:text-gray-900 hover:bg-gray-50 rounded-lg transition-colors"
            >
              {secondaryActionLabel}
            </button>
          )}
        </div>
      )}
    </div>
  );
}
