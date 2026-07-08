import React from 'react';

interface State {
  error: Error | null;
}

/**
 * Catches render errors so a single bad component doesn't white-screen the
 * whole app. Deliberately terse — no telemetry hook here since the app doesn't
 * have one wired up yet; a follow-up PR should send to Sentry-equivalent.
 */
export default class ErrorBoundary extends React.Component<
  { children: React.ReactNode },
  State
> {
  state: State = { error: null };

  static getDerivedStateFromError(error: Error): State {
    return { error };
  }

  componentDidCatch(error: Error, info: React.ErrorInfo) {
    // eslint-disable-next-line no-console
    console.error('[ErrorBoundary]', error, info.componentStack);
  }

  render() {
    if (this.state.error) {
      return (
        <div className="min-h-screen flex items-center justify-center p-8 bg-background">
          <div className="max-w-lg w-full border border-error/20 bg-error/5 rounded-card p-6 text-sm">
            <h1 className="text-lg font-bold text-error mb-2">Something went wrong</h1>
            <p className="text-text-secondary mb-4">
              The page hit an unexpected error and could not render. This has been logged.
            </p>
            <pre className="text-xs bg-white border border-border rounded p-3 overflow-auto max-h-64">
              {this.state.error.message}
            </pre>
            <button
              type="button"
              onClick={() => window.location.assign('/')}
              className="mt-4 px-3 py-2 bg-primary text-white rounded text-xs font-bold"
            >
              Return home
            </button>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}
