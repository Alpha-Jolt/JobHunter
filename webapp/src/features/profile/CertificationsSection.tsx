"use client";

import { useState } from "react";
import { Award, Pencil, Trash2, Loader2, ExternalLink } from "lucide-react";
import { CertificationEntry } from "@/shared/api/types";
import { profileApi } from "@/shared/api/gateway";
import { useProfileStore } from "@/shared/state/profileStore";
import { useUiStore } from "@/shared/state/uiStore";
import { SectionCard } from "./SectionCard";
import { ProfileFormModal } from "./ProfileFormModal";
import { Button } from "@/shared/components/Button";
import { Input } from "@/shared/components/Input";

export function CertificationsSection({ certifications }: { certifications: CertificationEntry[] }) {
  const { addToast } = useUiStore();
  const { updateSection } = useProfileStore();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [isDeleting, setIsDeleting] = useState<string | null>(null);
  const [editingId, setEditingId] = useState<string | null>(null);

  const [formData, setFormData] = useState<Omit<CertificationEntry, "cert_id" | "order_index">>({
    name: "",
    issuer: "",
    issued_date: "",
    expiry_date: "",
    credential_url: "",
  });

  const handleOpenModal = (cert?: CertificationEntry) => {
    if (cert) {
      setEditingId(cert.cert_id);
      setFormData({
        name: cert.name,
        issuer: cert.issuer || "",
        issued_date: cert.issued_date ? cert.issued_date.substring(0, 10) : null,
        expiry_date: cert.expiry_date ? cert.expiry_date.substring(0, 10) : null,
        credential_url: cert.credential_url || "",
      });
    } else {
      setEditingId(null);
      setFormData({
        name: "",
        issuer: "",
        issued_date: "",
        expiry_date: "",
        credential_url: "",
      });
    }
    setIsModalOpen(true);
  };

  const handleSave = async () => {
    if (!formData.name) {
      addToast("error", "Certification Name is required");
      return;
    }

    setIsSaving(true);
    try {
      const payload = {
        ...formData,
        issued_date: formData.issued_date ? new Date(formData.issued_date).toISOString() : null,
        expiry_date: formData.expiry_date ? new Date(formData.expiry_date).toISOString() : null,
      };

      let updatedCertifications: CertificationEntry[];
      
      if (editingId) {
        updatedCertifications = certifications.map((c) =>
          c.cert_id === editingId ? { ...c, ...payload } : c
        );
      } else {
        const newEntry = { ...payload, cert_id: crypto.randomUUID(), order_index: certifications.length };
        updatedCertifications = [...certifications, newEntry];
      }

      // Re-index
      updatedCertifications = updatedCertifications.map((c, idx) => ({ ...c, order_index: idx }));

      updateSection({ certifications: updatedCertifications });
      
      await profileApi.replaceCertifications(updatedCertifications.map(c => ({
        name: c.name,
        issuer: c.issuer,
        issued_date: c.issued_date,
        expiry_date: c.expiry_date,
        credential_url: c.credential_url,
        order_index: c.order_index
      })));
      
      addToast("success", editingId ? "Certification updated" : "Certification added");
      setIsModalOpen(false);
    } catch {
      updateSection({ certifications }); // Revert
      addToast("error", "Failed to save certification");
    } finally {
      setIsSaving(false);
    }
  };

  const handleDelete = async (id: string) => {
    setIsDeleting(id);
    try {
      const updatedCertifications = certifications
        .filter((c) => c.cert_id !== id)
        .map((c, idx) => ({ ...c, order_index: idx }));
        
      updateSection({ certifications: updatedCertifications });
      
      await profileApi.replaceCertifications(updatedCertifications.map(c => ({
        name: c.name,
        issuer: c.issuer,
        issued_date: c.issued_date,
        expiry_date: c.expiry_date,
        credential_url: c.credential_url,
        order_index: c.order_index
      })));
      
      addToast("success", "Certification deleted");
    } catch {
      updateSection({ certifications });
      addToast("error", "Failed to delete certification");
    } finally {
      setIsDeleting(null);
    }
  };

  return (
    <>
      <SectionCard title="Certifications" onAdd={() => handleOpenModal()}>
        {certifications.length === 0 ? (
          <div className="text-center py-6 text-muted-foreground">
            <Award className="h-12 w-12 mx-auto mb-3 opacity-20" />
            <p>No certifications added yet.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {certifications.map((cert) => (
              <div key={cert.cert_id} className="group relative flex gap-3 border border-border p-4 rounded-lg bg-card hover:border-primary/50 transition-colors">
                <div className="flex-none pt-0.5">
                  <div className="h-10 w-10 rounded-full bg-secondary flex items-center justify-center border border-border">
                    <Award className="h-5 w-5 text-primary" />
                  </div>
                </div>
                <div className="flex-1 min-w-0">
                  <h4 className="text-sm font-semibold text-foreground truncate" title={cert.name}>{cert.name}</h4>
                  <p className="text-xs text-foreground/80 mt-1">{cert.issuer}</p>
                  
                  <p className="text-xs text-muted-foreground mt-1">
                    {cert.issued_date ? `Issued ${new Date(cert.issued_date).toLocaleDateString(undefined, { month: 'short', year: 'numeric' })}` : ""}
                    {cert.expiry_date ? ` • Expires ${new Date(cert.expiry_date).toLocaleDateString(undefined, { month: 'short', year: 'numeric' })}` : ""}
                  </p>
                  
                  {cert.credential_url && (
                    <a href={cert.credential_url} target="_blank" rel="noopener noreferrer" className="inline-flex items-center gap-1 mt-2 text-xs font-medium text-primary hover:underline">
                      View Credential <ExternalLink className="h-3 w-3" />
                    </a>
                  )}
                </div>
                <div className="absolute right-2 top-2 opacity-0 group-hover:opacity-100 transition-opacity flex gap-1">
                  <Button variant="ghost" size="icon" onClick={() => handleOpenModal(cert)} className="h-7 w-7">
                    <Pencil className="h-3.5 w-3.5" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-7 w-7 text-destructive hover:text-destructive hover:bg-destructive/10"
                    onClick={() => handleDelete(cert.cert_id)}
                    disabled={isDeleting === cert.cert_id}
                  >
                    {isDeleting === cert.cert_id ? (
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
        title={editingId ? "Edit Certification" : "Add Certification"}
      >
        <div className="space-y-4">
          <div className="space-y-1">
            <label className="text-sm font-medium">Certification Name</label>
            <Input
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              placeholder="Ex: AWS Certified Solutions Architect"
            />
          </div>
          
          <div className="space-y-1">
            <label className="text-sm font-medium">Issuing Organization</label>
            <Input
              value={formData.issuer || ""}
              onChange={(e) => setFormData({ ...formData, issuer: e.target.value })}
              placeholder="Ex: Amazon Web Services"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-1">
              <label className="text-sm font-medium">Issue Date</label>
              <Input
                type="month"
                value={formData.issued_date ? formData.issued_date.slice(0, 7) : ""}
                onChange={(e) => setFormData({ ...formData, issued_date: e.target.value })}
              />
            </div>
            <div className="space-y-1">
              <label className="text-sm font-medium">Expiration Date</label>
              <Input
                type="month"
                value={formData.expiry_date ? formData.expiry_date.slice(0, 7) : ""}
                onChange={(e) => setFormData({ ...formData, expiry_date: e.target.value })}
              />
            </div>
          </div>

          <div className="space-y-1">
            <label className="text-sm font-medium">Credential URL</label>
            <Input
              value={formData.credential_url || ""}
              onChange={(e) => setFormData({ ...formData, credential_url: e.target.value })}
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
