"use client";
import { ResponsiveView } from "@/components/responsive-view";
import { useAnalyticsData } from "./use-analytics-data";
import { AnalyticsDesktopView } from "./analytics-desktop-view";
import { AnalyticsMobileView } from "./analytics-mobile-view";
export function AnalyticsPage() {
  const model = useAnalyticsData();
  return <ResponsiveView layout="chart" mobile={() => <AnalyticsMobileView {...model} />} desktop={() => <AnalyticsDesktopView {...model} />} />;
}
