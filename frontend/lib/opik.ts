/**
 * Opik (Comet) URL helpers for observability links.
 *
 * URL format: /opik/{workspace}/projects/{project_id}/traces/{trace_id}
 */

const OPIK_WORKSPACE = process.env.NEXT_PUBLIC_OPIK_WORKSPACE || 'default';
const OPIK_PROJECT_ID = process.env.NEXT_PUBLIC_OPIK_PROJECT_ID || '';
const OPIK_BASE_URL = 'https://www.comet.com/opik';

/**
 * Get the Opik dashboard URL for the project.
 */
export function getOpikDashboardUrl(): string {
    if (!OPIK_PROJECT_ID) {
        return `${OPIK_BASE_URL}/${OPIK_WORKSPACE}`;
    }
    return `${OPIK_BASE_URL}/${OPIK_WORKSPACE}/projects/${OPIK_PROJECT_ID}/traces`;
}

/**
 * Get the Opik trace URL for a specific trace.
 */
export function getOpikTraceUrl(traceId: string): string {
    if (!OPIK_PROJECT_ID) {
        // Fallback: just go to workspace if no project ID
        return `${OPIK_BASE_URL}/${OPIK_WORKSPACE}`;
    }
    return `${OPIK_BASE_URL}/${OPIK_WORKSPACE}/projects/${OPIK_PROJECT_ID}/traces/${traceId}`;
}

/**
 * Get the Opik experiments URL.
 */
export function getOpikExperimentsUrl(): string {
    if (!OPIK_PROJECT_ID) {
        return `${OPIK_BASE_URL}/${OPIK_WORKSPACE}`;
    }
    return `${OPIK_BASE_URL}/${OPIK_WORKSPACE}/projects/${OPIK_PROJECT_ID}/experiments`;
}

/**
 * Get the Opik datasets URL.
 */
export function getOpikDatasetsUrl(): string {
    if (!OPIK_PROJECT_ID) {
        return `${OPIK_BASE_URL}/${OPIK_WORKSPACE}`;
    }
    return `${OPIK_BASE_URL}/${OPIK_WORKSPACE}/projects/${OPIK_PROJECT_ID}/datasets`;
}

export const OPIK_CONFIG = {
    workspace: OPIK_WORKSPACE,
    projectId: OPIK_PROJECT_ID,
    baseUrl: OPIK_BASE_URL,
};
