import { createClient } from "./supabase/client";

export interface SyncPayload {
  id: string;
  type: "progress" | "xp" | "note" | "bookmark" | "preference" | "achievement";
  action: "upsert" | "delete";
  table: string;
  data: Record<string, unknown>;
  timestamp: number;
}

const QUEUE_STORAGE_KEY = "dsarena_offline_sync_queue";

class SyncService {
  private queue: SyncPayload[] = [];
  private isSyncing = false;

  constructor() {
    if (typeof window !== "undefined") {
      this.loadQueue();
      window.addEventListener("online", () => this.flushQueue());
    }
  }

  // Lazy getter — only creates the Supabase client when actually needed (in browser)
  private getSupabase() {
    return createClient();
  }

  private loadQueue() {
    try {
      const stored = localStorage.getItem(QUEUE_STORAGE_KEY);
      if (stored) {
        this.queue = JSON.parse(stored);
      }
    } catch {
      this.queue = [];
    }
  }

  private saveQueue() {
    try {
      localStorage.setItem(QUEUE_STORAGE_KEY, JSON.stringify(this.queue));
    } catch (err) {
      console.error("Failed to save sync queue:", err);
    }
  }

  public async enqueue(payload: Omit<SyncPayload, "id" | "timestamp">) {
    const item: SyncPayload = {
      ...payload,
      id: `${Date.now()}_${Math.random().toString(36).substring(2, 9)}`,
      timestamp: Date.now(),
    };

    this.queue.push(item);
    this.saveQueue();

    if (navigator.onLine) {
      await this.flushQueue();
    }
  }

  public async flushQueue() {
    if (this.isSyncing || this.queue.length === 0 || !navigator.onLine) return;

    this.isSyncing = true;
    const remaining: SyncPayload[] = [];
    const supabase = this.getSupabase();

    for (const item of this.queue) {
      try {
        let success = false;
        if (item.action === "upsert") {
          const { error } = await supabase.from(item.table).upsert(item.data);
          if (!error) success = true;
        } else if (item.action === "delete") {
          const { error } = await supabase.from(item.table).delete().match(item.data);
          if (!error) success = true;
        }

        if (!success) {
          remaining.push(item);
        }
      } catch (err) {
        console.error(`Sync error for ${item.table}:`, err);
        remaining.push(item);
      }
    }

    this.queue = remaining;
    this.saveQueue();
    this.isSyncing = false;
  }

  // Helper Methods for Specific Actions
  public async syncProgress(userId: string, nodeId: string, nodeType: string, completed: boolean, percentage: number) {
    const payload = {
      user_id: userId,
      node_id: nodeId,
      node_type: nodeType,
      completed,
      progress_percentage: percentage,
      updated_at: new Date().toISOString(),
    };

    await this.enqueue({
      type: "progress",
      action: "upsert",
      table: "user_progress",
      data: payload,
    });
  }

  public async syncNote(userId: string, lessonId: string, markdownContent: string) {
    const payload = {
      user_id: userId,
      lesson_id: lessonId,
      markdown_content: markdownContent,
      updated_at: new Date().toISOString(),
    };

    await this.enqueue({
      type: "note",
      action: "upsert",
      table: "notes",
      data: payload,
    });
  }

  public async syncBookmark(userId: string, targetType: string, targetId: string, title: string) {
    const payload = {
      user_id: userId,
      target_type: targetType,
      target_id: targetId,
      title,
    };

    await this.enqueue({
      type: "bookmark",
      action: "upsert",
      table: "bookmarks",
      data: payload,
    });
  }
}

export const syncService = new SyncService();
