"use client";

import { useState } from "react";
import { Trophy, Pencil, Trash2, Loader2, ExternalLink } from "lucide-react";
import { AchievementEntry } from "@/shared/api/types";
import { profileApi } from "@/shared/api/gateway";
import { useProfileStore } from "@/shared/state/profileStore";
import { useUiStore } from "@/shared/state/uiStore";
import { SectionCard } from "./SectionCard";
import { ProfileFormModal } from "./ProfileFormModal";
import { Button } from "@/shared/components/Button";
import { Input } from "@/shared/components/Input";

export function AchievementsSection({ achievements }: { achievements: AchievementEntry[] }) {
  const { addToast } = useUiStore();
  const { updateSection } = useProfileStore();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [isDeleting, setIsDeleting] = useState<string | null>(null);
  const [editingId, setEditingId] = useState<string | null>(null);

  const [formData, setFormData] = useState<Omit<AchievementEntry, "ach_id" | "order_index">>({
    title: "",
    description: "",
    date: "",
    url: "",
  });

  const handleOpenModal = (ach?: AchievementEntry) => {
    if (ach) {
      setEditingId(ach.ach_id);
      setFormData({
        title: ach.title,
        description: ach.description || "",
        date: ach.date ? ach.date.substring(0, 10) : null,
        url: ach.url || "",
      });
    } else {
      setEditingId(null);
      setFormData({
        title: "",
        description: "",
        date: "",
        url: "",
      });
    }
    setIsModalOpen(true);
  };

  const handleSave = async () => {
    if (!formData.title) {
      addToast("error", "Achievement Title is required");
      return;
    }

    setIsSaving(true);
    try {
      const payload = {
        ...formData,
        date: formData.date ? new Date(formData.date).toISOString() : null,
      };

      let updatedAchievements: AchievementEntry[];
      
      if (editingId) {
        updatedAchievements = achievements.map((a) =>
          a.ach_id === editingId ? { ...a, ...payload } : a
        );
      } else {
        const newEntry = { ...payload, ach_id: crypto.randomUUID(), order_index: achievements.length };
        updatedAchievements = [...achievements, newEntry];
      }

      // Re-index
      updatedAchievements = updatedAchievements.map((a, idx) => ({ ...a, order_index: idx }));

      updateSection({ achievements: updatedAchievements });
      
      await profileApi.replaceAchievements(updatedAchievements.map(a => ({
        title: a.title,
        description: a.description,
        date: a.date,
        url: a.url,
        order_index: a.order_index
      })));
      
      addToast("success", editingId ? "Achievement updated" : "Achievement added");
      setIsModalOpen(false);
    } catch {
      updateSection({ achievements }); // Revert
      addToast("error", "Failed to save achievement");
    } finally {
      setIsSaving(false);
    }
  };

  const handleDelete = async (id: string) => {
    setIsDeleting(id);
    try {
      const updatedAchievements = achievements
        .filter((a) => a.ach_id !== id)
        .map((a, idx) => ({ ...a, order_index: idx }));
        
      updateSection({ achievements: updatedAchievements });
      
      await profileApi.replaceAchievements(updatedAchievements.map(a => ({
        title: a.title,
        description: a.description,
        date: a.date,
        url: a.url,
        order_index: a.order_index
      })));
      
      addToast("success", "Achievement deleted");
    } catch {
      updateSection({ achievements });
      addToast("error", "Failed to delete achievement");
    } finally {
      setIsDeleting(null);
    }
  };

  return (
    <>
      <SectionCard title="Honors & Achievements" onAdd={() => handleOpenModal()}>
        {achievements.length === 0 ? (
          <div className="text-center py-6 text-muted-foreground">
            <Trophy className="h-12 w-12 mx-auto mb-3 opacity-20" />
            <p>No honors or achievements added yet.</p>
          </div>
        ) : (
          <div className="space-y-4">
            {achievements.map((ach) => (
              <div key={ach.ach_id} className="group relative flex gap-3 border-b border-border/50 pb-4 last:pb-0 last:border-0">
                <div className="flex-none pt-0.5">
                  <div className="h-8 w-8 rounded-full bg-secondary flex items-center justify-center">
                    <Trophy className="h-4 w-4 text-primary" />
                  </div>
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <h4 className="text-sm font-semibold text-foreground">{ach.title}</h4>
                    {ach.date && (
                      <span className="text-xs text-muted-foreground whitespace-nowrap">
                        • {new Date(ach.date).toLocaleDateString(undefined, { month: 'short', year: 'numeric' })}
                      </span>
                    )}
                  </div>
                  
                  {ach.description && (
                    <p className="text-sm text-foreground/80 mt-1 whitespace-pre-line">
                      {ach.description}
                    </p>
                  )}
                  
                  {ach.url && (
                    <a href={ach.url} target="_blank" rel="noopener noreferrer" className="inline-flex items-center gap-1 mt-2 text-xs font-medium text-primary hover:underline">
                      View Link <ExternalLink className="h-3 w-3" />
                    </a>
                  )}
                </div>
                <div className="absolute right-0 top-0 opacity-0 group-hover:opacity-100 transition-opacity flex gap-1">
                  <Button variant="ghost" size="icon" onClick={() => handleOpenModal(ach)} className="h-7 w-7">
                    <Pencil className="h-3.5 w-3.5" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-7 w-7 text-destructive hover:text-destructive hover:bg-destructive/10"
                    onClick={() => handleDelete(ach.ach_id)}
                    disabled={isDeleting === ach.ach_id}
                  >
                    {isDeleting === ach.ach_id ? (
                      <Loader2 className="h-3.5 w-3.5 animate-spin" />
                    ) : (
                      <Trash2 className="h-3.5 w-3.5" />
                    )}
                  </Button>
                </div>
              </div>
            ))}
          </div>
        )}
      </SectionCard>

      <ProfileFormModal
        open={isModalOpen}
        onOpenChange={setIsModalOpen}
        title={editingId ? "Edit Achievement" : "Add Achievement"}
      >
        <div className="space-y-4">
          <div className="space-y-1">
            <label className="text-sm font-medium">Title</label>
            <Input
              value={formData.title}
              onChange={(e) => setFormData({ ...formData, title: e.target.value })}
              placeholder="Ex: Employee of the Year"
            />
          </div>
          
          <div className="space-y-1">
            <label className="text-sm font-medium">Date (Optional)</label>
            <Input
              type="month"
              value={formData.date ? formData.date.slice(0, 7) : ""}
              onChange={(e) => setFormData({ ...formData, date: e.target.value })}
            />
          </div>

          <div className="space-y-1">
            <label className="text-sm font-medium">Description (Optional)</label>
            <textarea
              value={formData.description || ""}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              className="flex min-h-[100px] w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-sm placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
              placeholder="Describe what you accomplished..."
            />
          </div>

          <div className="space-y-1">
            <label className="text-sm font-medium">Link URL (Optional)</label>
            <Input
              value={formData.url || ""}
              onChange={(e) => setFormData({ ...formData, url: e.target.value })}
              placeholder="https://..."
            />
          </div>

          <div className="flex justify-end gap-2 pt-4">
            <Button variant="outline" onClick={() => setIsModalOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleSave} disabled={isSaving}>
              {isSaving ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}
              Save
            </Button>
          </div>
        </div>
      </ProfileFormModal>
    </>
  );
}
