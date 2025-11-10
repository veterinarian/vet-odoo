/** @odoo-module **/

import {registry} from "@web/core/registry";
import {Component, onWillStart, onWillUpdateProps, useState} from "@odoo/owl";
import {useService} from "@web/core/utils/hooks";
import {standardFieldProps} from "@web/views/fields/standard_field_props";
import {_t} from "@web/core/l10n/translation";

export class MedicalTimelineField extends Component {
    static template = "vet_clinic.MedicalTimelineRenderer";
    static props = {
        ...standardFieldProps,
    };

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.state = useState({
            records: [],
            expandedIds: new Set(),
        });

        onWillStart(async () => {
            await this.loadRecords();
        });

        onWillUpdateProps(async (nextProps) => {
            if (nextProps.value !== this.props.value) {
                await this.loadRecords();
            }
        });
    }

    async loadRecords() {
        // In Odoo 17, one2many fields contain record list objects
        const recordList = this.props.record.data[this.props.name];

        if (!recordList || recordList.length === 0) {
            this.state.records = [];
            return;
        }

        // Extract IDs and fetch full data via ORM
        const ids = recordList.records.map((rec) => rec.resId);

        const records = await this.orm.read("vet.medical.note", ids, [
            "id",
            "name",
            "date",
            "patient_id",
            "booking_id",
            "author_id",
            "note_type",
            "subjective",
            "objective",
            "assessment",
            "plan",
            "content",
            "is_important",
            "is_private",
            "attachment_count",
        ]);

        // Fetch patient's owner for each record
        for (const record of records) {
            if (record.patient_id && record.patient_id[0]) {
                const patient = await this.orm.read(
                    "vet.patient",
                    [record.patient_id[0]],
                    ["owner_id"]
                );
                record.owner_id = patient[0].owner_id;
            }
        }

        // Sort by date descending
        records.sort((a, b) => {
            const dateA = new Date(a.date);
            const dateB = new Date(b.date);
            return dateB - dateA;
        });

        this.state.records = records;
    }

    onHeaderClick(ev) {
        const recordId = parseInt(ev.currentTarget.dataset.recordId, 10);
        this.toggleExpand(recordId);
    }

    onOpenRecord(ev) {
        const recordId = parseInt(ev.currentTarget.dataset.recordId, 10);
        this.openRecord(recordId);
    }

    toggleExpand(recordId) {
        if (this.state.expandedIds.has(recordId)) {
            this.state.expandedIds.delete(recordId);
        } else {
            this.state.expandedIds.add(recordId);
        }
    }

    isExpanded(recordId) {
        return this.state.expandedIds.has(recordId);
    }

    formatDateTime(dateString) {
        if (!dateString) return "";
        // Treat as UTC
        const date = new Date(dateString + "Z");
        return date.toLocaleString(undefined, {
            year: "numeric",
            month: "short",
            day: "numeric",
            hour: "2-digit",
            minute: "2-digit",
        });
    }

    getNoteTypeLabel(noteType) {
        const types = {
            soap: "SOAP Note",
            communication: "Communication",
            internal: "Internal Note",
            result: "Diagnostic Result",
            image: "Image/Photo",
            report: "Report",
        };
        return types[noteType] || noteType;
    }

    getDisplayName(field) {
        if (!field) return "";
        return Array.isArray(field) ? field[1] : field;
    }

    openRecord(recordId) {
        this.action.doAction({
            type: "ir.actions.act_window",
            res_model: "vet.medical.note",
            res_id: recordId,
            views: [[false, "form"]],
            target: "current",
        });
    }
}

export const medicalTimelineField = {
    component: MedicalTimelineField,
    displayName: _t("Medical Timeline"),
    supportedTypes: ["one2many"],
};

registry.category("fields").add("medical_timeline", medicalTimelineField);
