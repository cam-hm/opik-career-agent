"use client";

import React, { createContext, useContext, useState, useEffect } from 'react';
import { en, LocaleType } from '@/locales/en';

type Language = 'en';
type LocalizedData = string | Record<string, string> | null | undefined;

interface LanguageContextType {
    language: Language;
    setLanguage: (lang: Language) => void;
    t: (key: string) => string;
    getLocalized: (data: LocalizedData) => string;
}

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

export function LanguageProvider({ children }: { children: React.ReactNode }) {
    // Hardcode to English
    const language: Language = 'en';

    // No-op setter
    const setLanguage = (lang: Language) => {
        console.log("Language is fixed to English");
    };

    const getNestedValue = (obj: Record<string, any>, path: string): any => {
        return path.split('.').reduce((acc, part) => acc && acc[part], obj) || path;
    };

    const t = (key: string): string => {
        // Always use English dictionary
        const dict = en;
        const value = getNestedValue(dict, key);
        return typeof value === 'string' ? value : key;
    };

    const getLocalized = (data: LocalizedData): string => {
        if (!data) return "";
        if (typeof data === 'string') return data;
        if (typeof data === 'object') {
            return data['en'] || "";
        }
        return "";
    };

    return (
        <LanguageContext.Provider value={{ language, setLanguage, t, getLocalized }}>
            {children}
        </LanguageContext.Provider>
    );
}

export const useLanguage = () => {
    const context = useContext(LanguageContext);
    if (!context) {
        throw new Error('useLanguage must be used within a LanguageProvider');
    }
    return context;
};
