"use client";

import { useState } from "react";
import type { ProfileInput } from "@/lib/api";
import { Button, Card, Checkbox, Field, Fieldset, Select } from "@/components/ui";
import sx from "./sections.module.css";

const ANNEX_III_AREAS = [
  "biometrics",
  "critical_infrastructure",
  "education",
  "employment",
  "essential_services",
  "credit_scoring",
  "life_health_insurance",
  "law_enforcement",
  "migration_border",
  "justice_democracy",
];

export function QuestionnaireForm({
  onSubmit,
  busy,
}: {
  onSubmit: (profile: ProfileInput) => void;
  busy: boolean;
}) {
  const [role, setRole] = useState<"provider" | "deployer">("provider");
  const [area, setArea] = useState("employment");
  const [deployerType, setDeployerType] = useState("public_body");
  const [annexIEmbedded, setAnnexIEmbedded] = useState(false);
  const [isGpai, setIsGpai] = useState(false);
  const [interacts, setInteracts] = useState(false);
  const [synthetic, setSynthetic] = useState(false);

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    onSubmit({
      role,
      annex_iii_area: area === "none" ? null : area,
      deployer_type: role === "deployer" ? deployerType : null,
      annex_i_embedded: annexIEmbedded,
      is_gpai: isGpai,
      interacts_with_humans: interacts,
      generates_synthetic_content: synthetic,
      content_lifecycle: synthetic ? "new" : null,
    });
  }

  return (
    <Card title="Questionnaire">
      <form className={sx.form} onSubmit={handleSubmit}>
        <div className={sx.formGrid}>
          <Field label="Operator role" htmlFor="role">
            <Select
              id="role"
              value={role}
              onChange={(e) => setRole(e.target.value as "provider" | "deployer")}
            >
              <option value="provider">Provider</option>
              <option value="deployer">Deployer</option>
            </Select>
          </Field>
          <Field label="Annex III high-risk area" htmlFor="area">
            <Select id="area" value={area} onChange={(e) => setArea(e.target.value)}>
              <option value="none">none</option>
              {ANNEX_III_AREAS.map((a) => (
                <option key={a} value={a}>
                  {a}
                </option>
              ))}
            </Select>
          </Field>
        </div>

        {role === "deployer" && (
          <Field label="Deployer type (relevant to the FRIA, Art. 27)" htmlFor="deployer-type">
            <Select
              id="deployer-type"
              value={deployerType}
              onChange={(e) => setDeployerType(e.target.value)}
            >
              <option value="public_body">public_body</option>
              <option value="private_public_service">private_public_service</option>
              <option value="other">other</option>
            </Select>
          </Field>
        )}

        <Fieldset legend="Signals">
          <Checkbox label="Annex I embedded (product safety)" checked={annexIEmbedded} onChange={setAnnexIEmbedded} />
          <Checkbox label="General-purpose AI (GPAI)" checked={isGpai} onChange={setIsGpai} />
          <Checkbox label="Interacts with humans (Art. 50(1))" checked={interacts} onChange={setInteracts} />
          <Checkbox label="Generates synthetic content (Art. 50(2))" checked={synthetic} onChange={setSynthetic} />
        </Fieldset>

        <div className={sx.actions}>
          <Button type="submit" busy={busy}>
            {busy ? "Classifying…" : "Classify"}
          </Button>
        </div>
      </form>
    </Card>
  );
}
