/**
 * API Helper with Authentication
 * 
 * This module provides fetch wrapper that automatically includes
 * Clerk JWT token in the Authorization header.
 */

import { auth } from "@clerk/nextjs/server";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

/**
 * Get API base URL without trailing slash
 */
export function getApiUrl(): string {
    return API_BASE_URL.replace(/\/$/, "");
}

/**
 * Fetch wrapper for client-side API calls with authentication
 * Use this in components with useAuth() hook
 */
export async function fetchWithAuth(
    endpoint: string,
    options: RequestInit = {},
    getToken: () => Promise<string | null>
): Promise<Response> {
    const token = await getToken();
    const apiUrl = getApiUrl();

    const headers: HeadersInit = {
        ...options.headers,
    };

    if (token) {
        (headers as Record<string, string>)["Authorization"] = `Bearer ${token}`;
    }

    return fetch(`${apiUrl}${endpoint}`, {
        ...options,
        headers,
    });
}

/**
 * Fetch wrapper for client-side without needing token function
 * Uses raw fetch with manual token
 */
export async function apiRequest(
    endpoint: string,
    options: RequestInit = {},
    token?: string | null
): Promise<Response> {
    const apiUrl = getApiUrl();

    const headers: HeadersInit = {
        ...options.headers,
    };

    if (token) {
        (headers as Record<string, string>)["Authorization"] = `Bearer ${token}`;
    }

    return fetch(`${apiUrl}${endpoint}`, {
        ...options,
        headers,
    });
}
