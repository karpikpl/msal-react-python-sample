import React, { useState } from 'react';

import { PageLayout } from './components/PageLayout';
import { loginRequest, apiTokenRequest } from './authConfig';
import { callMsGraph } from './graph';
import { callApi } from './api';
import { ProfileData } from './components/ProfileData';

import { AuthenticatedTemplate, UnauthenticatedTemplate, useMsal } from '@azure/msal-react';
import './App.css';
import Button from 'react-bootstrap/Button';

/**
 * Renders information about the signed-in user or a button to retrieve data about the user
 */

const ProfileContent = () => {
    const { instance, accounts } = useMsal();
    const [graphData, setGraphData] = useState(null);

    function RequestProfileData() {
        // Silently acquires an access token which is then attached to a request for MS Graph data
        instance
            .acquireTokenSilent({
                ...loginRequest,
                account: accounts[0],
            })
            .then((response) => {
                callMsGraph(response.accessToken).then((response) => setGraphData(response));
            });
    }

    return (
        <>
            <h5 className="profileContent">Welcome {accounts[0].name}</h5>
            {graphData ? (
                <ProfileData graphData={graphData} />
            ) : (
                <Button variant="secondary" onClick={RequestProfileData}>
                    Request Profile
                </Button>
            )}
        </>
    );
};

const ApiContent = () => {
    const { instance, accounts } = useMsal();
    const [apiData, setApiData] = useState(null);

    function RequestApiData() {
        // Silently acquires an access token which is then attached to a request for API data
        instance
            .acquireTokenSilent({
                ...apiTokenRequest,
                account: accounts[0],
            })
            .then((response) => {
                callApi(response.accessToken).then((response) => setApiData(response));
            });
    }

    return (
        <>
            <h5 className="profileContent">Welcome {accounts[0].name}</h5>
            {apiData ? (
                <pre>{JSON.stringify(apiData, null, 2)}</pre> // Stringify and format the JSON data for display
            ) : (
                <Button variant="secondary" onClick={RequestApiData}>
                    Call Api
                </Button>
            )}
        </>
    );
};

/**
 * If a user is authenticated the ProfileContent component above is rendered. Otherwise a message indicating a user is not authenticated is rendered.
 */
const MainContent = () => {
    return (
        <div className="App">
            <AuthenticatedTemplate>
                <ProfileContent />
                <ApiContent />
            </AuthenticatedTemplate>

            <UnauthenticatedTemplate>
                <h5 className="card-title">Please sign-in to see your profile information.</h5>
            </UnauthenticatedTemplate>
        </div>
    );
};

export default function App() {
    return (
        <PageLayout>
            <MainContent />
        </PageLayout>
    );
}
