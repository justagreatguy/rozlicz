"""KSeF (Krajowy System e-Faktur) API client.

Polish National e-Invoice System integration.
Documentation: https://ksef.mf.gov.pl
"""

import base64
from datetime import datetime
from typing import Any

import httpx
import structlog
from lxml import etree

from app.config import settings

logger = structlog.get_logger()


class KSeFClient:
    """KSeF API client for e-invoice operations."""

    def __init__(self) -> None:
        """Initialize KSeF client."""
        self.base_url = (
            settings.KSEF_SANDBOX_URL
            if settings.KSEF_USE_SANDBOX
            else settings.KSEF_API_URL
        )
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=60.0,
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
        )
        self._session_token: str | None = None

    async def __aenter__(self) -> "KSeFClient":
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()

    async def close(self) -> None:
        """Close HTTP client."""
        await self.client.aclose()

    async def authenticate(
        self,
        nip: str,
        authorization_token: str,
    ) -> str:
        """Authenticate with KSeF and get session token.

        Args:
            nip: Polish Tax ID Number (NIP)
            authorization_token: KSeF authorization token

        Returns:
            Session token for subsequent requests
        """
        # TODO: Implement actual KSeF authentication
        # This is a placeholder for the token-based authentication flow
        logger.info("ksef_authenticate", nip=nip)

        try:
            # KSeF API authentication endpoint
            response = await self.client.post(
                "/api/online/Session/AuthorisationToken",
                json={
                    "nip": nip,
                    "authorizationToken": authorization_token,
                },
            )
            response.raise_for_status()
            data = response.json()
            self._session_token = data.get("sessionToken")
            return self._session_token
        except httpx.HTTPError as e:
            logger.error("ksef_authenticate_failed", error=str(e), nip=nip)
            raise KSeFError(f"Authentication failed: {e}") from e

    async def send_invoice(self, invoice_xml: str | bytes) -> dict:
        """Send invoice to KSeF.

        Args:
            invoice_xml: Invoice in FA_V2 XML format

        Returns:
            KSeF response with reference number
        """
        if not self._session_token:
            raise KSeFError("Not authenticated. Call authenticate() first.")

        logger.info("ksef_send_invoice")

        try:
            response = await self.client.post(
                "/api/online/Invoice/Send",
                headers={
                    "SessionToken": self._session_token,
                    "Content-Type": "application/octet-stream",
                },
                content=invoice_xml if isinstance(invoice_xml, bytes) else invoice_xml.encode(),
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error("ksef_send_invoice_failed", error=str(e))
            raise KSeFError(f"Failed to send invoice: {e}") from e

    async def get_invoice(self, ksef_reference: str) -> bytes:
        """Get invoice from KSeF by reference number.

        Args:
            ksef_reference: KSeF reference number

        Returns:
            Invoice XML content
        """
        if not self._session_token:
            raise KSeFError("Not authenticated. Call authenticate() first.")

        logger.info("ksef_get_invoice", ksef_reference=ksef_reference)

        try:
            response = await self.client.get(
                f"/api/online/Invoice/Get/{ksef_reference}",
                headers={"SessionToken": self._session_token},
            )
            response.raise_for_status()
            return response.content
        except httpx.HTTPError as e:
            logger.error("ksef_get_invoice_failed", error=str(e))
            raise KSeFError(f"Failed to get invoice: {e}") from e

    async def query_invoices(
        self,
        date_from: datetime,
        date_to: datetime,
        page_size: int = 100,
        page_offset: int = 0,
    ) -> dict:
        """Query invoices from KSeF.

        Args:
            date_from: Start date
            date_to: End date
            page_size: Number of results per page
            page_offset: Page offset

        Returns:
            List of invoices matching criteria
        """
        if not self._session_token:
            raise KSeFError("Not authenticated. Call authenticate() first.")

        logger.info("ksef_query_invoices", date_from=date_from, date_to=date_to)

        try:
            response = await self.client.post(
                "/api/online/Invoice/Query",
                headers={"SessionToken": self._session_token},
                json={
                    "queryCriteria": {
                        "dateFrom": date_from.isoformat(),
                        "dateTo": date_to.isoformat(),
                    },
                    "pageSize": page_size,
                    "pageOffset": page_offset,
                },
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error("ksef_query_invoices_failed", error=str(e))
            raise KSeFError(f"Failed to query invoices: {e}") from e

    async def get_upo(self, ksef_reference: str) -> bytes:
        """Get UPO (Urzędowe Poświadczenie Odbioru) for invoice.

        Args:
            ksef_reference: KSeF reference number

        Returns:
            UPO PDF document
        """
        if not self._session_token:
            raise KSeFError("Not authenticated. Call authenticate() first.")

        logger.info("ksef_get_upo", ksef_reference=ksef_reference)

        try:
            response = await self.client.get(
                f"/api/online/Invoice/Get/Upo/{ksef_reference}",
                headers={"SessionToken": self._session_token},
            )
            response.raise_for_status()
            return response.content
        except httpx.HTTPError as e:
            logger.error("ksef_get_upo_failed", error=str(e))
            raise KSeFError(f"Failed to get UPO: {e}") from e

    @staticmethod
    def generate_invoice_xml(
        seller_nip: str,
        buyer_nip: str | None,
        invoice_number: str,
        issue_date: datetime,
        gross_amount: float,
        items: list[dict],
    ) -> str:
        """Generate FA_V2 compliant invoice XML.

        This is a simplified generator. In production, use a proper
        XML template with full schema compliance.
        """
        # TODO: Implement proper FA_V2 XML generation
        # For now, return a skeleton structure
        nsmap = {
            None: "http://crd.gov.pl/wzor/2023/06/29/12648/",
            "xsi": "http://www.w3.org/2001/XMLSchema-instance",
        }

        root = etree.Element("Faktura", nsmap=nsmap)
        etree.SubElement(root, "Numer").text = invoice_number
        etree.SubElement(root, "DataWystawienia").text = issue_date.strftime("%Y-%m-%d")

        sprzedawca = etree.SubElement(root, "Sprzedawca")
        etree.SubElement(sprzedawca, "NIP").text = seller_nip

        if buyer_nip:
            nabywca = etree.SubElement(root, "Nabywca")
            etree.SubElement(nabywca, "NIP").text = buyer_nip

        return etree.tostring(root, pretty_print=True, encoding="unicode")


class KSeFError(Exception):
    """KSeF client error."""

    pass
