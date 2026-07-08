"use client";

import { useState } from "react";
import { Plus, Loader2, Globe, Trash2 } from "lucide-react";
import { LanguageEntry } from "@/shared/api/types";
import { profileApi } from "@/shared/api/gateway";
import { useProfileStore } from "@/shared/state/profileStore";
import { useUiStore } from "@/shared/state/uiStore";
import { SectionCard } from "./SectionCard";
import { Button } from "@/shared/components/Button";
import { Input } from "@/shared/components/Input";

export function LanguagesSection({ languages }: { languages: LanguageEntry[] }) {
  const { addToast } = useUiStore();
  const { updateSection } = useProfileStore();
  const [isSaving, setIsSaving] = useState(false);
  
  const [showForm, setShowForm] = useState(false);
  const [newName, setNewName] = useState("");
  const [newProficiency, setNewProficiency] = useState("");

  const handleAdd = async () => {
    if (!newName.trim()) return;

    setIsSaving(true);
    try {
      const newEntry: LanguageEntry = {
        lang_id: crypto.randomUUID(), // Optimistic ID
        name: newName.trim(),
        proficiency: newProficiency.trim() || null,
        order_index: languages.length,
      };

      const updatedLanguages = [...languages, newEntry];
      
      updateSection({ languages: updatedLanguages });
      
      await profileApi.replaceLanguages(updatedLanguages.map(l => ({
        name: l.name,
        proficiency: l.proficiency,
        order_index: l.order_index
      })));
      
      setNewName("");
      setNewProficiency("");
      setShowForm(false);
      addToast("success", "Language added");
    } catch {
      updateSection({ languages });
      addToast("error", "Failed to add language");
    } finally {
      setIsSaving(false);
    }
  };

  const handleRemove = async (id: string) => {
    setIsSaving(true);
    try {
      const updatedLanguages = languages.filter((l) => l.lang_id !== id).map((l, idx) => ({ ...l, order_index: idx }));
      
      updateSection({ languages: updatedLanguages });
      
      await profileApi.replaceLanguages(updatedLanguages.map(l => ({
        name: l.name,
        proficiency: l.proficiency,
        order_index: l.order_index
      })));
      
    } catch {
      updateSection({ languages });
      addToast("error", "Failed to remove language");
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <SectionCard 
      title="Languages" 
      onAdd={() => setShowForm(true)}
    >
      <div className="space-y-4">
        {languages.length === 0 && !showForm ? (
          <div className="text-center py-6 text-muted-foreground">
            <Globe className="h-12 w-12 mx-auto mb-3 opacity-20" />
            <p>No languages added yet.</p>
          </div>
        ) : (
          <div className="flex flex-col gap-2">
            {languages.map((lang) => (
              <div 
                key={lang.lang_id}
                className="group flex items-center justify-between p-3 border border-border rounded-lg bg-card hover:border-primary/50 transition-colors"
              >
                <div>
                  <span className="font-medium text-foreground">{lang.name}</span>
                  {lang.proficiency && (
                    <span className="text-sm text-muted-foreground ml-2">
                      ({lang.proficiency})
                    </span>
                  )}
                </div>
                <button
                  onClick={() => handleRemove(lang.lang_id)}
                  disabled={isSaving}
                  className="p-1.5 rounded-md hover:bg-destructive/10 text-muted-foreground hover:text-destructive opacity-0 group-hover:opacity-100 transition-opacity"
                >
                  <Trash2 className="h-4 w-4" />
                </button>
              </div>
            ))}
          </div>
        )}

        {showForm && (
          <div className="bg-muted/50 p-4 rounded-lg border border-border space-y-3 mt-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <Input
                placeholder="Language (e.g. French, Spanish)"
                value={newName}
                onChange={(e) => setNewName(e.target.value)}
                autoFocus
                onKeyDown={(e) => {
                  if (e.key === "Enter") handleAdd();
                  if (e.key === "Escape") setShowForm(false);
                }}
              />
              <select
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                value={newProficiency}
                onChange={(e) => setNewProficiency(e.target.value)}
              >
                <option value="">Select Proficiency</option>
                <option value="Native or Bilingual">Native or Bilingual</option>
                <option value="Fluent">Fluent</option>
                <option value="Professional Working">Professional Working</option>
                <option value="Conversational">Conversational</option>
                <option value="Elementary">Elementary</option>
              </select>
            </div>
            <div className="flex justify-end gap-2">
              <Button variant="ghost" size="sm" onClick={() => setShowForm(false)}>
                Cancel
              </Button>
              <Button size="sm" onClick={handleAdd} disabled={isSaving || !newName.trim()}>
                {isSaving ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Plus className="mr-2 h-4 w-4" />}
                Add Language
              </Button>
            </div>
          </div>
        )}
      </div>
    </SectionCard>
  );
}
