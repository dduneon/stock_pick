# frontend/app

## OVERVIEW
Next.js 15 App Router pages - stock listing, search, and detail views.

## FILES
- `page.tsx` - Home page
- `stocks/page.tsx` - Stock listing
- `search/page.tsx` - Search functionality  
- `stock/[ticker]/page.tsx` - Individual stock detail
- `layout.tsx` - Root layout with providers

## WHERE TO LOOK
| Task | File |
|------|------|
| Add new page | Create in `app/` subdirectory |
| Modify stock detail | `stock/[ticker]/page.tsx` |

## CONVENTIONS
- Use React Server Components by default
- Client components marked with `'use client'`
- Tailwind CSS for styling
- CVA (class-variance-authority) for component variants

## ANTI-PATTERNS
- NO `as any` type assertions
- NO inline styles - use Tailwind
