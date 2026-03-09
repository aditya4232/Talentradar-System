import axios from "axios";

const API_BASE_URL = "http://localhost:8000/api/v1";

export interface Candidate {
  id: number;
  name: string;
  current_title: string;
  company: string;
  location: string;
  experience_years: number;
  skills: string[];
  summary: string;
  talent_score: number;
  source: string;
  email?: string;
  phone?: string;
  profile_url?: string;
}

export interface ScraperStatus {
  active: boolean;
  message: string;
  current_target: string;
  candidates_found: number;
  engine: string;
  last_update: number;
}

export const fetchCandidates = async (): Promise<Candidate[]> => {
  try {
    const response = await axios.get(`${API_BASE_URL}/candidates`);
    return response.data;
  } catch (error) {
    console.error("Error fetching candidates:", error);
    return [];
  }
};

export const startScraper = async (url?: string) => {
  try {
    if (url) {
      const response = await axios.post(`${API_BASE_URL}/scraper/scrape-url`, { url });
      return response.data;
    }
    const response = await axios.post(`${API_BASE_URL}/scraper/run`);
    return response.data;
  } catch (error) {
    console.error("Error starting scraper:", error);
    throw error;
  }
};

export const stopScraper = async () => {
  try {
    const response = await axios.post(`${API_BASE_URL}/scraper/stop`);
    return response.data;
  } catch (error) {
    console.error("Error stopping scraper:", error);
    throw error;
  }
};

export const getScraperStatus = async (): Promise<ScraperStatus> => {
  try {
    const response = await axios.get(`${API_BASE_URL}/scraper/status`);
    return response.data;
  } catch (error) {
    console.error("Error getting scraper status:", error);
    throw error;
  }
};

export const resetDatabase = async () => {
  try {
    const response = await axios.post(`${API_BASE_URL}/scraper/reset`);
    return response.data;
  } catch (error) {
    console.error("Error resetting database:", error);
    throw error;
  }
};
