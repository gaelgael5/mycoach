package com.mycoach.app.models

import android.os.Parcelable
import com.google.gson.annotations.SerializedName
import kotlinx.parcelize.Parcelize

// ── Client ──────────────────────────────────────────────────

@Parcelize
data class Client(
    val id: Int = 0,
    val name: String,
    val email: String? = null,
    val phone: String? = null,
    val notes: String? = null,
    @SerializedName("hourly_rate") val hourlyRate: Double = 0.0,
    @SerializedName("total_hours") val totalHours: Double = 0.0,
    @SerializedName("total_revenue") val totalRevenue: Double = 0.0,
    @SerializedName("total_paid") val totalPaid: Double = 0.0,
    val balance: Double = 0.0,
) : Parcelable

data class ClientRequest(
    val name: String,
    val email: String? = null,
    val phone: String? = null,
    val notes: String? = null,
    @SerializedName("hourly_rate") val hourlyRate: Double = 0.0,
)

// ── Session ──────────────────────────────────────────────────

@Parcelize
data class Session(
    val id: Int = 0,
    @SerializedName("client_id") val clientId: Int,
    @SerializedName("client_name") val clientName: String = "",
    val date: String,
    @SerializedName("duration_minutes") val durationMinutes: Int,
    val notes: String? = null,
    val billed: Boolean = true,
    val amount: Double = 0.0,
) : Parcelable

data class SessionRequest(
    @SerializedName("client_id") val clientId: Int,
    val date: String,
    @SerializedName("duration_minutes") val durationMinutes: Int,
    val notes: String? = null,
    val billed: Boolean = true,
)

// ── Payment ──────────────────────────────────────────────────

@Parcelize
data class Payment(
    val id: Int = 0,
    @SerializedName("client_id") val clientId: Int,
    @SerializedName("client_name") val clientName: String = "",
    val date: String,
    val amount: Double,
    val method: String? = null,
    val notes: String? = null,
) : Parcelable

data class PaymentRequest(
    @SerializedName("client_id") val clientId: Int,
    val date: String,
    val amount: Double,
    val method: String? = null,
    val notes: String? = null,
)

// ── Dashboard ────────────────────────────────────────────────

data class DashboardStats(
    @SerializedName("total_clients") val totalClients: Int,
    @SerializedName("total_sessions") val totalSessions: Int,
    @SerializedName("total_hours") val totalHours: Double,
    @SerializedName("total_revenue") val totalRevenue: Double,
    @SerializedName("total_paid") val totalPaid: Double,
    @SerializedName("total_outstanding") val totalOutstanding: Double,
)

// ── Calendar ─────────────────────────────────────────────────

data class CalendarEvent(
    val id: String,
    val title: String,
    val start: String,
    val end: String,
    val description: String = "",
    @SerializedName("html_link") val htmlLink: String = "",
)

data class CalendarEventRequest(
    val title: String,
    val start: String,
    @SerializedName("duration_minutes") val durationMinutes: Int,
    val description: String = "",
)

data class CalendarStatus(val connected: Boolean)

// ── Generic API response ─────────────────────────────────────

data class ApiResponse(val id: Int? = null, val message: String = "")
