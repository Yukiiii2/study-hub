"use client";

import { PageHeader } from "@/components/page-header";
import { SectionHeader, StatusBadge } from "@/components/study-ui";
import { useAuth } from "@/features/auth/auth-provider";
import { useResourceTimezone } from "@/features/resources/use-resource-timezone";

export function SettingsPage() {
  const { user } = useAuth();
  const { timezone, timezoneNote, timezoneFailed, retryTimezone } = useResourceTimezone();
  return <>
    <PageHeader title="Settings" description="Your account and study workspace information." />
    <div className="settings-layout">
      <section className="ui-panel" aria-labelledby="settings-account"><SectionHeader title="Account" titleId="settings-account" actions={<StatusBadge tone="success">Signed in</StatusBadge>} />
        <dl className="settings-facts"><div><dt>Email</dt><dd>{user?.email ?? "Email unavailable"}</dd></div></dl>
        <p className="resource-note">Your workspace administrator manages account access. Use the Account menu to sign out on this device.</p>
      </section>
      <section className="ui-panel" aria-labelledby="settings-timezone"><SectionHeader title="Study timezone" titleId="settings-timezone" />
        <dl className="settings-facts"><div><dt>Displayed timezone</dt><dd>{timezone}</dd></div></dl>
        <p className="resource-note">{timezoneNote}</p>
        {timezoneFailed && <button type="button" className="secondary-button" onClick={retryTimezone}>Retry timezone</button>}
        <p className="resource-note">Calendar dates, review deadlines and study reports use your saved profile timezone.</p>
      </section>
      <section className="ui-panel settings-workspace" aria-labelledby="settings-workspace"><SectionHeader title="Study Hub workspace" titleId="settings-workspace" />
        <p className="resource-note">CPALE review, organized around your curriculum, study plan and learning sources.</p>
        <dl className="settings-facts"><div><dt>Appearance</dt><dd>Dark study workspace</dd></div><div><dt>Study data</dt><dd>Saved to your account</dd></div></dl>
      </section>
    </div>
  </>;
}
