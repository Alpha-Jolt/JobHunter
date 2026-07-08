"use client";

import { useState } from "react";
import { Pencil, Trash2, Loader2, Briefcase } from "lucide-react";
import { ExperienceEntry } from "@/shared/api/types";
import { profileApi } from "@/shared/api/gateway";
import { useProfileStore } from "@/shared/state/profileStore";
import { useUiStore } from "@/shared/state/uiStore";
import { SectionCard } from "./SectionCard";
import { ProfileFormModal } from "./ProfileFormModal";
import { Button } from "@/shared/components/Button";
import { Input } from "@/shared/components/Input";

export function ExperienceSection({ experiences }: { experiences: ExperienceEntry[] }) {
  const { addToast } = useUiStore();
  const { updateSection } = useProfileStore();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [isDeleting, setIsDeleting] = useState<string | null>(null);
  const [editingId, setEditingId] = useState<string | null>(null);

  const [formData, setFormData] = useState<Omit<ExperienceEntry, "exp_id" | "order_index">>({
    company: "",
    title: "",
    start_date: "",
    end_date: "",
    is_current: false,
    description: "",
    location: "",
  });

  const handleOpenModal = (exp?: ExperienceEntry) => {
    if (exp) {
      setEditingId(exp.exp_id);
      setFormData({
        company: exp.company,
        title: exp.title,
        start_date: exp.start_date ? exp.start_date.substring(0, 10) : null,
        end_date: exp.end_date ? exp.end_date.substring(0, 10) : null,
        is_current: exp.is_current,
        description: exp.description || "",
        location: exp.location || "",
      });
    } else {
      setEditingId(null);
      setFormData({
        company: "",
        title: "",
        start_date: "",
        end_date: "",
        is_current: false,
        description: "",
        location: "",
      });
    }
    setIsModalOpen(true);
  };

  const handleSave = async () => {
    if (!formData.company || !formData.title) {
      addToast("error", "Company and Title are required");
      return;
    }

    setIsSaving(true);
    try {
      const payload = {
        ...formData,
        start_date: formData.start_date ? new Date(formData.start_date).toISOString() : null,
        end_date: formData.is_current || !formData.end_date ? null : new Date(formData.end_date).toISOString(),
        order_index: experiences.length,
      };

      if (editingId) {
        await profileApi.updateExperience(editingId, payload);
        updateSection({
          experiences: experiences.map((e) =>
            e.exp_id === editingId ? { ...e, ...payload } : e
          ),
        });
        addToast("success", "Experience updated");
      } else {
        const res = await profileApi.addExperience(payload);
        updateSection({
          experiences: [...experiences, { ...payload, exp_id: res.exp_id }],
        });
        addToast("success", "Experience added");
      }
      setIsModalOpen(false);
    } catch {
      addToast("error", "Failed to save experience");
    } finally {
      setIsSaving(false);
    }
  };

  const handleDelete = async (id: string) => {
    setIsDeleting(id);
    try {
      await profileApi.deleteExperience(id);
      updateSection({
        experiences: experiences.filter((e) => e.exp_id !== id),
      });
      addToast("success", "Experience deleted");
    } catch {
      addToast("error", "Failed to delete experience");
    } finally {
      setIsDeleting(null);
    }
  };

  return (
    <>
      <SectionCard title="Experience" onAdd={() => handleOpenModal()}>
        {experiences.length === 0 ? (
          <div className="text-center py-6 text-muted-foreground">
            <Briefcase className="h-12 w-12 mx-auto mb-3 opacity-20" />
            <p>No experience added yet.</p>
          </div>
        ) : (
          <div className="space-y-6">
            {experiences.map((exp) => (
              <div key={exp.exp_id} className="group relative flex gap-4">
                <div className="flex-none pt-1">
                  <div className="h-12 w-12 rounded-lg bg-secondary flex items-center justify-center border border-border">
                    <Briefcase className="h-6 w-6 text-muted-foreground" />
                  </div>
                </div>
                <div className="flex-1">
                  <h4 className="text-base font-semibold text-foreground">{exp.title}</h4>
                  <p className="text-sm font-medium text-foreground/80">{exp.company}</p>
                  <p className="text-sm text-muted-foreground mt-0.5">
                    {exp.start_date ? new Date(exp.start_date).toLocaleDateString(undefined, { month: 'short', year: 'numeric' }) : "Unknown"} -{" "}
                    {exp.is_current
                      ? "Present"
                      : exp.end_date
                        ? new Date(exp.end_date).toLocaleDateString(undefined, { month: 'short', year: 'numeric' })
                        : "Unknown"}
                    {exp.location && ` • ${exp.location}`}
                  </p>
                  {exp.description && (
                    <p className="text-sm text-foreground/80 mt-2 whitespace-pre-line">
                      {exp.description}
                    </p>
                  )}
                </div>
                <div className="absolute right-0 top-0 opacity-0 group-hover:opacity-100 transition-opacity flex gap-2">
                  <Button variant="ghost" size="icon" onClick={() => handleOpenModal(exp)}>
                    <Pencil className="h-4 w-4" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="text-destructive hover:text-destructive hover:bg-destructive/10"
                    onClick={() => handleDelete(exp.exp_id)}
                    disabled={isDeleting === exp.exp_id}
                  >
                    {isDeleting === exp.exp_id ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      <Trash2 className="h-4 w-4" />
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
        title={editingId ? "Edit Experience" : "Add Experience"}
      >
        <div className="space-y-4">
          <div className="space-y-1">
            <label className="text-sm font-medium">Title</label>
            <Input
              value={formData.title}
              onChange={(e) => setFormData({ ...formData, title: e.target.value })}
              placeholder="Ex: Software Engineer"
            />
          </div>
          <div className="space-y-1">
            <label className="text-sm font-medium">Company</label>
            <Input
              value={formData.company}
              onChange={(e) => setFormData({ ...formData, company: e.target.value })}
              placeholder="Ex: Microsoft"
            />
          </div>
          <div className="space-y-1">
            <label className="text-sm font-medium">Location</label>
            <Input
              value={formData.location || ""}
              onChange={(e) => setFormData({ ...formData, location: e.target.value })}
              placeholder="Ex: London, UK"
            />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-1">
              <label className="text-sm font-medium">Start Date</label>
              <Input
                type="month"
                value={formData.start_date ? formData.start_date.slice(0, 7) : ""}
                onChange={(e) => setFormData({ ...formData, start_date: e.target.value })}
              />
            </div>
            <div className="space-y-1">
              <label className="text-sm font-medium">End Date</label>
              <Input
                type="month"
                value={formData.end_date ? formData.end_date.slice(0, 7) : ""}
                onChange={(e) => setFormData({ ...formData, end_date: e.target.value })}
                disabled={formData.is_current}
              />
            </div>
          </div>
          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              id="is_current"
              checked={formData.is_current}
              onChange={(e) => setFormData({ ...formData, is_current: e.target.checked })}
              className="rounded border-input"
            />
            <label htmlFor="is_current" className="text-sm font-medium cursor-pointer">
              I currently work here
            </label>
          </div>
          <div className="space-y-1">
            <label className="text-sm font-medium">Description</label>
            <textarea
              value={formData.description || ""}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              className="flex min-h-[100px] w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-sm placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
              placeholder="Describe your responsibilities and achievements..."
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
