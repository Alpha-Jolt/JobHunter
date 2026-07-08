"use client";

import { useState } from "react";
import { GraduationCap, Pencil, Trash2, Loader2 } from "lucide-react";
import { EducationEntry } from "@/shared/api/types";
import { profileApi } from "@/shared/api/gateway";
import { useProfileStore } from "@/shared/state/profileStore";
import { useUiStore } from "@/shared/state/uiStore";
import { SectionCard } from "./SectionCard";
import { ProfileFormModal } from "./ProfileFormModal";
import { Button } from "@/shared/components/Button";
import { Input } from "@/shared/components/Input";

export function EducationSection({ education }: { education: EducationEntry[] }) {
  const { addToast } = useUiStore();
  const { updateSection } = useProfileStore();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [isDeleting, setIsDeleting] = useState<string | null>(null);
  const [editingId, setEditingId] = useState<string | null>(null);

  const [formData, setFormData] = useState<Omit<EducationEntry, "edu_id" | "order_index">>({
    institution: "",
    degree: "",
    field: "",
    start_year: null,
    end_year: null,
    grade: "",
    description: "",
  });

  const handleOpenModal = (edu?: EducationEntry) => {
    if (edu) {
      setEditingId(edu.edu_id);
      setFormData({
        institution: edu.institution,
        degree: edu.degree || "",
        field: edu.field || "",
        start_year: edu.start_year,
        end_year: edu.end_year,
        grade: edu.grade || "",
        description: edu.description || "",
      });
    } else {
      setEditingId(null);
      setFormData({
        institution: "",
        degree: "",
        field: "",
        start_year: null,
        end_year: null,
        grade: "",
        description: "",
      });
    }
    setIsModalOpen(true);
  };

  const handleSave = async () => {
    if (!formData.institution) {
      addToast("error", "Institution is required");
      return;
    }

    setIsSaving(true);
    try {
      const payload = {
        ...formData,
        order_index: education.length,
      };

      if (editingId) {
        await profileApi.updateEducation(editingId, payload);
        updateSection({
          education: education.map((e) =>
            e.edu_id === editingId ? { ...e, ...payload } : e
          ),
        });
        addToast("success", "Education updated");
      } else {
        const res = await profileApi.addEducation(payload);
        updateSection({
          education: [...education, { ...payload, edu_id: res.edu_id }],
        });
        addToast("success", "Education added");
      }
      setIsModalOpen(false);
    } catch {
      addToast("error", "Failed to save education");
    } finally {
      setIsSaving(false);
    }
  };

  const handleDelete = async (id: string) => {
    setIsDeleting(id);
    try {
      await profileApi.deleteEducation(id);
      updateSection({
        education: education.filter((e) => e.edu_id !== id),
      });
      addToast("success", "Education deleted");
    } catch {
      addToast("error", "Failed to delete education");
    } finally {
      setIsDeleting(null);
    }
  };

  return (
    <>
      <SectionCard title="Education" onAdd={() => handleOpenModal()}>
        {education.length === 0 ? (
          <div className="text-center py-6 text-muted-foreground">
            <GraduationCap className="h-12 w-12 mx-auto mb-3 opacity-20" />
            <p>No education added yet.</p>
          </div>
        ) : (
          <div className="space-y-6">
            {education.map((edu) => (
              <div key={edu.edu_id} className="group relative flex gap-4">
                <div className="flex-none pt-1">
                  <div className="h-12 w-12 rounded-lg bg-secondary flex items-center justify-center border border-border">
                    <GraduationCap className="h-6 w-6 text-muted-foreground" />
                  </div>
                </div>
                <div className="flex-1">
                  <h4 className="text-base font-semibold text-foreground">
                    {edu.institution}
                  </h4>
                  <p className="text-sm font-medium text-foreground/80">
                    {edu.degree} {edu.field && `in ${edu.field}`}
                  </p>
                  <p className="text-sm text-muted-foreground mt-0.5">
                    {edu.start_year || "Unknown"} - {edu.end_year || "Present"}
                    {edu.grade && ` • Grade: ${edu.grade}`}
                  </p>
                  {edu.description && (
                    <p className="text-sm text-foreground/80 mt-2 whitespace-pre-line">
                      {edu.description}
                    </p>
                  )}
                </div>
                <div className="absolute right-0 top-0 opacity-0 group-hover:opacity-100 transition-opacity flex gap-2">
                  <Button variant="ghost" size="icon" onClick={() => handleOpenModal(edu)}>
                    <Pencil className="h-4 w-4" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="text-destructive hover:text-destructive hover:bg-destructive/10"
                    onClick={() => handleDelete(edu.edu_id)}
                    disabled={isDeleting === edu.edu_id}
                  >
                    {isDeleting === edu.edu_id ? (
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
        title={editingId ? "Edit Education" : "Add Education"}
      >
        <div className="space-y-4">
          <div className="space-y-1">
            <label className="text-sm font-medium">Institution</label>
            <Input
              value={formData.institution}
              onChange={(e) => setFormData({ ...formData, institution: e.target.value })}
              placeholder="Ex: Stanford University"
            />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-1">
              <label className="text-sm font-medium">Degree</label>
              <Input
                value={formData.degree || ""}
                onChange={(e) => setFormData({ ...formData, degree: e.target.value })}
                placeholder="Ex: Bachelor of Science"
              />
            </div>
            <div className="space-y-1">
              <label className="text-sm font-medium">Field of Study</label>
              <Input
                value={formData.field || ""}
                onChange={(e) => setFormData({ ...formData, field: e.target.value })}
                placeholder="Ex: Computer Science"
              />
            </div>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-1">
              <label className="text-sm font-medium">Start Year</label>
              <Input
                type="number"
                value={formData.start_year || ""}
                onChange={(e) => setFormData({ ...formData, start_year: e.target.value ? parseInt(e.target.value) : null })}
                placeholder="YYYY"
              />
            </div>
            <div className="space-y-1">
              <label className="text-sm font-medium">End Year (or expected)</label>
              <Input
                type="number"
                value={formData.end_year || ""}
                onChange={(e) => setFormData({ ...formData, end_year: e.target.value ? parseInt(e.target.value) : null })}
                placeholder="YYYY"
              />
            </div>
          </div>
          <div className="space-y-1">
            <label className="text-sm font-medium">Grade / GPA</label>
            <Input
              value={formData.grade || ""}
              onChange={(e) => setFormData({ ...formData, grade: e.target.value })}
              placeholder="Ex: 3.8 / 4.0"
            />
          </div>
          <div className="space-y-1">
            <label className="text-sm font-medium">Description (Optional)</label>
            <textarea
              value={formData.description || ""}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              className="flex min-h-[100px] w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-sm placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
              placeholder="Activities, societies, honors..."
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
