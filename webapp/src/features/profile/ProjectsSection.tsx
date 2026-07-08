"use client";

import { useState } from "react";
import { FolderGit2, Pencil, Trash2, Loader2, ExternalLink } from "lucide-react";
import { ProjectEntry } from "@/shared/api/types";
import { profileApi } from "@/shared/api/gateway";
import { useProfileStore } from "@/shared/state/profileStore";
import { useUiStore } from "@/shared/state/uiStore";
import { SectionCard } from "./SectionCard";
import { ProfileFormModal } from "./ProfileFormModal";
import { Button } from "@/shared/components/Button";
import { Input } from "@/shared/components/Input";

export function ProjectsSection({ projects }: { projects: ProjectEntry[] }) {
  const { addToast } = useUiStore();
  const { updateSection } = useProfileStore();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [isDeleting, setIsDeleting] = useState<string | null>(null);
  const [editingId, setEditingId] = useState<string | null>(null);

  const [formData, setFormData] = useState<Omit<ProjectEntry, "proj_id" | "order_index">>({
    title: "",
    description: "",
    url: "",
    repo_url: "",
    skills: [],
  });

  const [skillInput, setSkillInput] = useState("");

  const handleOpenModal = (proj?: ProjectEntry) => {
    if (proj) {
      setEditingId(proj.proj_id);
      setFormData({
        title: proj.title,
        description: proj.description || "",
        url: proj.url || "",
        repo_url: proj.repo_url || "",
        skills: proj.skills || [],
      });
    } else {
      setEditingId(null);
      setFormData({
        title: "",
        description: "",
        url: "",
        repo_url: "",
        skills: [],
      });
    }
    setSkillInput("");
    setIsModalOpen(true);
  };

  const handleAddSkill = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && skillInput.trim()) {
      e.preventDefault();
      if (!formData.skills.includes(skillInput.trim())) {
        setFormData({
          ...formData,
          skills: [...formData.skills, skillInput.trim()],
        });
      }
      setSkillInput("");
    }
  };

  const handleRemoveSkill = (skillToRemove: string) => {
    setFormData({
      ...formData,
      skills: formData.skills.filter((s) => s !== skillToRemove),
    });
  };

  const handleSave = async () => {
    if (!formData.title) {
      addToast("error", "Project Title is required");
      return;
    }

    setIsSaving(true);
    try {
      const payload = {
        ...formData,
        order_index: projects.length,
      };

      if (editingId) {
        await profileApi.updateProject(editingId, payload);
        updateSection({
          projects: projects.map((p) =>
            p.proj_id === editingId ? { ...p, ...payload } : p
          ),
        });
        addToast("success", "Project updated");
      } else {
        const res = await profileApi.addProject(payload);
        updateSection({
          projects: [...projects, { ...payload, proj_id: res.proj_id }],
        });
        addToast("success", "Project added");
      }
      setIsModalOpen(false);
    } catch {
      addToast("error", "Failed to save project");
    } finally {
      setIsSaving(false);
    }
  };

  const handleDelete = async (id: string) => {
    setIsDeleting(id);
    try {
      await profileApi.deleteProject(id);
      updateSection({
        projects: projects.filter((p) => p.proj_id !== id),
      });
      addToast("success", "Project deleted");
    } catch {
      addToast("error", "Failed to delete project");
    } finally {
      setIsDeleting(null);
    }
  };

  return (
    <>
      <SectionCard title="Projects" onAdd={() => handleOpenModal()}>
        {projects.length === 0 ? (
          <div className="text-center py-6 text-muted-foreground">
            <FolderGit2 className="h-12 w-12 mx-auto mb-3 opacity-20" />
            <p>No projects added yet.</p>
          </div>
        ) : (
          <div className="space-y-6">
            {projects.map((proj) => (
              <div key={proj.proj_id} className="group relative flex gap-4 border border-border p-4 rounded-lg bg-card/50">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <FolderGit2 className="h-5 w-5 text-muted-foreground" />
                    <h4 className="text-base font-semibold text-foreground">{proj.title}</h4>
                  </div>
                  
                  {proj.description && (
                    <p className="text-sm text-foreground/80 mt-2 mb-3 whitespace-pre-line">
                      {proj.description}
                    </p>
                  )}

                  {proj.skills && proj.skills.length > 0 && (
                    <div className="flex flex-wrap gap-1.5 mb-3">
                      {proj.skills.map(skill => (
                        <span key={skill} className="px-2 py-0.5 bg-secondary text-secondary-foreground rounded text-xs font-medium border border-border/50">
                          {skill}
                        </span>
                      ))}
                    </div>
                  )}

                  <div className="flex gap-4 mt-2">
                    {proj.url && (
                      <a href={proj.url} target="_blank" rel="noopener noreferrer" className="flex items-center gap-1.5 text-xs text-primary hover:underline">
                        <ExternalLink className="h-3.5 w-3.5" /> Live Demo
                      </a>
                    )}
                    {proj.repo_url && (
                      <a href={proj.repo_url} target="_blank" rel="noopener noreferrer" className="flex items-center gap-1.5 text-xs text-foreground/70 hover:text-foreground">
                        <FolderGit2 className="h-3.5 w-3.5" /> Repository
                      </a>
                    )}
                  </div>
                </div>
                <div className="absolute right-2 top-2 opacity-0 group-hover:opacity-100 transition-opacity flex flex-col gap-1">
                  <Button variant="ghost" size="icon" onClick={() => handleOpenModal(proj)} className="h-8 w-8">
                    <Pencil className="h-4 w-4" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-8 w-8 text-destructive hover:text-destructive hover:bg-destructive/10"
                    onClick={() => handleDelete(proj.proj_id)}
                    disabled={isDeleting === proj.proj_id}
                  >
                    {isDeleting === proj.proj_id ? (
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
        title={editingId ? "Edit Project" : "Add Project"}
      >
        <div className="space-y-4">
          <div className="space-y-1">
            <label className="text-sm font-medium">Project Title</label>
            <Input
              value={formData.title}
              onChange={(e) => setFormData({ ...formData, title: e.target.value })}
              placeholder="Ex: E-commerce Platform"
            />
          </div>
          
          <div className="space-y-1">
            <label className="text-sm font-medium">Description</label>
            <textarea
              value={formData.description || ""}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              className="flex min-h-[100px] w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-sm placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
              placeholder="What did you build? What problems did it solve?"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-1">
              <label className="text-sm font-medium">Project URL (Live)</label>
              <Input
                value={formData.url || ""}
                onChange={(e) => setFormData({ ...formData, url: e.target.value })}
                placeholder="https://..."
              />
            </div>
            <div className="space-y-1">
              <label className="text-sm font-medium">Repository URL</label>
              <Input
                value={formData.repo_url || ""}
                onChange={(e) => setFormData({ ...formData, repo_url: e.target.value })}
                placeholder="https://github.com/..."
              />
            </div>
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium">Tech Stack / Skills</label>
            <Input
              value={skillInput}
              onChange={(e) => setSkillInput(e.target.value)}
              onKeyDown={handleAddSkill}
              placeholder="Type a skill and press Enter (e.g. React, Node.js)"
            />
            {formData.skills.length > 0 && (
              <div className="flex flex-wrap gap-2 mt-2">
                {formData.skills.map((skill) => (
                  <span
                    key={skill}
                    className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-secondary text-secondary-foreground text-sm"
                  >
                    {skill}
                    <button
                      type="button"
                      onClick={() => handleRemoveSkill(skill)}
                      className="text-muted-foreground hover:text-foreground"
                    >
                      &times;
                    </button>
                  </span>
                ))}
              </div>
            )}
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
