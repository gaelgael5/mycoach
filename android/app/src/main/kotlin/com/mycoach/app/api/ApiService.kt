package com.mycoach.app.api

import com.mycoach.app.models.*
import retrofit2.Response
import retrofit2.http.*

interface ApiService {

    // ── Dashboard ────────────────────────────────────────────
    @GET("api/dashboard")
    suspend fun getDashboard(): DashboardStats

    // ── Clients ──────────────────────────────────────────────
    @GET("api/clients")
    suspend fun getClients(): List<Client>

    @GET("api/clients/{id}")
    suspend fun getClient(@Path("id") id: Int): Client

    @POST("api/clients")
    suspend fun createClient(@Body client: ClientRequest): ApiResponse

    @PUT("api/clients/{id}")
    suspend fun updateClient(@Path("id") id: Int, @Body client: ClientRequest): ApiResponse

    @DELETE("api/clients/{id}")
    suspend fun deleteClient(@Path("id") id: Int): ApiResponse

    // ── Sessions ─────────────────────────────────────────────
    @GET("api/sessions")
    suspend fun getSessions(@Query("client_id") clientId: Int? = null): List<Session>

    @POST("api/sessions")
    suspend fun createSession(@Body session: SessionRequest): ApiResponse

    @DELETE("api/sessions/{id}")
    suspend fun deleteSession(@Path("id") id: Int): ApiResponse

    // ── Payments ─────────────────────────────────────────────
    @GET("api/payments")
    suspend fun getPayments(@Query("client_id") clientId: Int? = null): List<Payment>

    @POST("api/payments")
    suspend fun createPayment(@Body payment: PaymentRequest): ApiResponse

    @DELETE("api/payments/{id}")
    suspend fun deletePayment(@Path("id") id: Int): ApiResponse

    // ── Calendar ─────────────────────────────────────────────
    @GET("api/calendar/status")
    suspend fun getCalendarStatus(): CalendarStatus

    @GET("api/calendar/events")
    suspend fun getCalendarEvents(@Query("days") days: Int = 14): List<CalendarEvent>

    @POST("api/calendar/events")
    suspend fun createCalendarEvent(@Body event: CalendarEventRequest): CalendarEvent

    @DELETE("api/calendar/events/{eventId}")
    suspend fun deleteCalendarEvent(@Path("eventId") eventId: String): ApiResponse
}
