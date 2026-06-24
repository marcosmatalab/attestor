"use client";

import { useState } from "react";
import type { ProfileInput } from "@/lib/api";
import { useLocale } from "@/lib/i18n/LocaleProvider";
import { Button, Card, Checkbox, Field, Fieldset, Select } from "@/components/ui";
import sx from "./sections.module.css";

// option VALUE (sent to the API, never translated) -> dictionary key for its DISPLAYED label
const AREA_LABEL_KEYS: Record<string, string> = {
  biometrics: "questionnaire.areaBiometrics",
  critical_infrastructure: "questionnaire.areaCriticalInfrastructure",
  education: "questionnaire.areaEducation",
  employment: "questionnaire.areaEmployment",
  essential_services: "questionnaire.areaEssentialServices",
  credit_scoring: "questionnaire.areaCreditScoring",
  life_health_insurance: "questionnaire.areaLifeHealthInsurance",
  law_enforcement: "questionnaire.areaLawEnforcement",
  migration_border: "questionnaire.areaMigrationBorder",
  justice_democracy: "questionnaire.areaJusticeDemocracy",
};
const ANNEX_III_AREAS = Object.keys(AREA_LABEL_KEYS);

const DEPLOYER_TYPE_LABEL_KEYS: Record<string, string> = {
  public_body: "questionnaire.deployerTypePublicBody",
  private_public_service: "questionnaire.deployerTypePrivatePublicService",
  other: "questionnaire.deployerTypeOther",
};

export function QuestionnaireForm({
  onSubmit,
  busy,
}: {
  onSubmit: (profile: ProfileInput) => void;
  busy: boolean;
}) {
  const { t } = useLocale();
  const [role, setRole] = useState<"provider" | "deployer">("provider");
  const [area, setArea] = useState("employment");
  const [deployerType, setDeployerType] = useState("public_body");
  const [annexIEmbedded, setAnnexIEmbedded] = useState(false);
  const [isGpai, setIsGpai] = useState(false);
  const [interacts, setInteracts] = useState(false);
  const [synthetic, setSynthetic] = useState(false);

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    // Values are the canonical engine inputs — translation only touches the labels above.
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
    <Card title={t("questionnaire.title")}>
      <form className={sx.form} onSubmit={handleSubmit}>
        <div className={sx.formGrid}>
          <Field label={t("questionnaire.roleLabel")} htmlFor="role">
            <Select
              id="role"
              value={role}
              onChange={(e) => setRole(e.target.value as "provider" | "deployer")}
            >
              <option value="provider">{t("questionnaire.roleProvider")}</option>
              <option value="deployer">{t("questionnaire.roleDeployer")}</option>
            </Select>
          </Field>
          <Field label={t("questionnaire.areaLabel")} htmlFor="area">
            <Select id="area" value={area} onChange={(e) => setArea(e.target.value)}>
              <option value="none">{t("questionnaire.areaNone")}</option>
              {ANNEX_III_AREAS.map((a) => (
                <option key={a} value={a}>
                  {t(AREA_LABEL_KEYS[a])}
                </option>
              ))}
            </Select>
          </Field>
        </div>

        {role === "deployer" && (
          <Field label={t("questionnaire.deployerTypeLabel")} htmlFor="deployer-type">
            <Select
              id="deployer-type"
              value={deployerType}
              onChange={(e) => setDeployerType(e.target.value)}
            >
              {Object.entries(DEPLOYER_TYPE_LABEL_KEYS).map(([value, key]) => (
                <option key={value} value={value}>
                  {t(key)}
                </option>
              ))}
            </Select>
          </Field>
        )}

        <Fieldset legend={t("questionnaire.signals")}>
          <Checkbox
            label={t("questionnaire.signalAnnexIEmbedded")}
            checked={annexIEmbedded}
            onChange={setAnnexIEmbedded}
          />
          <Checkbox label={t("questionnaire.signalGpai")} checked={isGpai} onChange={setIsGpai} />
          <Checkbox
            label={t("questionnaire.signalInteracts")}
            checked={interacts}
            onChange={setInteracts}
          />
          <Checkbox
            label={t("questionnaire.signalSynthetic")}
            checked={synthetic}
            onChange={setSynthetic}
          />
        </Fieldset>

        <div className={sx.actions}>
          <Button type="submit" busy={busy}>
            {busy ? t("questionnaire.submitting") : t("questionnaire.submit")}
          </Button>
        </div>
      </form>
    </Card>
  );
}
