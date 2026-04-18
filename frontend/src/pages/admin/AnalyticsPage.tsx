import { useQuery } from "@tanstack/react-query";
import { adminApi } from "../../api/client";
import { AdminAnalyticsOverview } from "../../components/admin/AdminAnalyticsOverview";
import { PageTransition } from "../../components/ui/PageTransition";
import { Skeleton } from "../../components/ui/Skeleton";

export function AnalyticsPage() {
  const analytics = useQuery({ queryKey: ["admin-analytics"], queryFn: adminApi.analytics });

  return (
    <PageTransition>
      <div className="space-y-6">
        <section className="flex flex-col gap-2">
          <p className="text-sm font-semibold uppercase text-brand-700">Analytics</p>
          <h1 className="text-2xl font-semibold text-ink">Support health and KB performance</h1>
          <p className="max-w-2xl text-sm leading-6 text-muted">
            Use these signals to spot support bottlenecks, improve article quality, and balance technician workload.
          </p>
        </section>

        {analytics.isLoading ? <Skeleton className="h-[520px]" /> : <AdminAnalyticsOverview data={analytics.data} />}
      </div>
    </PageTransition>
  );
}
