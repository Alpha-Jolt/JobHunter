"use client";

import { useState } from "react";
import { Plus, X, Loader2, Wrench } from "lucide-react";
import { SkillEntry } from "@/shared/api/types";
import { profileApi } from "@/shared/api/gateway";
import { useProfileStore } from "@/shared/state/profileStore";
import { useUiStore } from "@/shared/state/uiStore";
import { SectionCard } from "./SectionCard";
import { Button } from "@/shared/components/Button";
import { Input } from "@/shared/components/Input";

export function SkillsSection({ skills }: { skills: SkillEntry[] }) {
  const { addToast } = useUiStore();
  const { updateSection } = useProfileStore();
  const [isSaving, setIsSaving] = useState(false);
  
  const [showForm, setShowForm] = useState(false);
  const [newSkill, setNewSkill] = useState("");
  const [newCategory, setNewCategory] = useState("");
  const [newProficiency, setNewProficiency] = useState("");

  const handleAdd = async () => {
    if (!newSkill.trim()) return;

    setIsSaving(true);
    try {
      const newEntry: SkillEntry = {
        skill_id: crypto.randomUUID(), // Optimistic ID
        name: newSkill.trim(),
        category: newCategory.trim() || null,
        proficiency: newProficiency.trim() || null,
        order_index: skills.length,
      };

      const updatedSkills = [...skills, newEntry];
      
      // Store optimistic update
      updateSection({ skills: updatedSkills });
      
      // API call (replaces all)
      await profileApi.replaceSkills(updatedSkills.map(s => ({
        name: s.name,
        category: s.category,
        proficiency: s.proficiency,
        order_index: s.order_index
      })));
      
      setNewSkill("");
      setShowForm(false);
      addToast("success", "Skill added");
    } catch {
      // Revert on failure
      updateSection({ skills });
      addToast("error", "Failed to add skill");
    } finally {
      setIsSaving(false);
    }
  };

  const handleRemove = async (id: string) => {
    setIsSaving(true);
    try {
      const updatedSkills = skills.filter((s) => s.skill_id !== id).map((s, idx) => ({ ...s, order_index: idx }));
      
      updateSection({ skills: updatedSkills });
      
      await profileApi.replaceSkills(updatedSkills.map(s => ({
        name: s.name,
        category: s.category,
        proficiency: s.proficiency,
        order_index: s.order_index
      })));
      
    } catch {
      updateSection({ skills });
      addToast("error", "Failed to remove skill");
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <SectionCard 
      title="Skills" 
      onAdd={() => setShowForm(true)}
    >
      <div className="space-y-4">
        {skills.length === 0 && !showForm ? (
          <div className="text-center py-6 text-muted-foreground">
            <Wrench className="h-12 w-12 mx-auto mb-3 opacity-20" />
            <p>No skills added yet.</p>
          </div>
        ) : (
          <div className="flex flex-wrap gap-2">
            {skills.map((skill) => (
              <div 
                key={skill.skill_id}
                className="group flex items-center gap-2 bg-secondary text-secondary-foreground pl-3 pr-1.5 py-1.5 rounded-full text-sm font-medium border border-border"
              >
                <span>{skill.name}</span>
                {skill.proficiency && (
                  <span className="text-xs text-muted-foreground border-l border-border/50 pl-2">
                    {skill.proficiency}
                  </span>
                )}
                <button
                  onClick={() => handleRemove(skill.skill_id)}
                  disabled={isSaving}
                  className="ml-1 p-0.5 rounded-full hover:bg-destructive/10 hover:text-destructive opacity-50 group-hover:opacity-100 transition-opacity"
                >
                  <X className="h-3.5 w-3.5" />
                </button>
              </div>
            ))}
          </div>
        )}

        {showForm && (
          <div className="bg-muted/50 p-4 rounded-lg border border-border space-y-3 mt-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              <Input
                placeholder="Skill name (e.g. React)"
                value={newSkill}
                onChange={(e) => setNewSkill(e.target.value)}
                autoFocus
                onKeyDown={(e) => {
                  if (e.key === "Enter") handleAdd();
                  if (e.key === "Escape") setShowForm(false);
                }}
              />
              <Input
                placeholder="Category (Optional)"
                value={newCategory}
                onChange={(e) => setNewCategory(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleAdd()}
              />
              <select
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                value={newProficiency}
                onChange={(e) => setNewProficiency(e.target.value)}
              >
                <option value="">Select Proficiency (Optional)</option>
                <option value="Beginner">Beginner</option>
                <option value="Intermediate">Intermediate</option>
                <option value="Advanced">Advanced</option>
                <option value="Expert">Expert</option>
              </select>
            </div>
            <div className="flex justify-end gap-2">
              <Button variant="ghost" size="sm" onClick={() => setShowForm(false)}>
                Cancel
              </Button>
              <Button size="sm" onClick={handleAdd} disabled={isSaving || !newSkill.trim()}>
                {isSaving ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Plus className="mr-2 h-4 w-4" />}
                Add Skill
              </Button>
            </div>
          </div>
        )}
      </div>
    </SectionCard>
  );
}
