import { QueryClient } from "@tanstack/react-query";

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      suspense: true,
      staleTime: 24 * 60 * 60 * 1000, // 24 hours (forces revalidation, mostly useful to prevent eternally stale data)
      gcTime: 120 * 1000, // GC inactive queries every 2 minutes (results are pretty big)
    },
  },
});

export function getQueryClient() {
  return queryClient;
}
